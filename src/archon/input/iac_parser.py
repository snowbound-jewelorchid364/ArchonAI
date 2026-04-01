from __future__ import annotations
import io
import json
import yaml
from .base import InputParser, ParsedInput


class IaCParser(InputParser):
    async def parse(self, source: str | bytes) -> ParsedInput:
        content = source if isinstance(source, str) else source.decode()

        stripped = content.strip()
        is_cfn = stripped.startswith("{") or "AWSTemplateFormatVersion" in content

        if is_cfn:
            return self._parse_cloudformation(content)
        else:
            return self._parse_terraform(content)

    def _parse_cloudformation(self, content: str) -> ParsedInput:
        try:
            if content.strip().startswith("{"):
                data = json.loads(content)
            else:
                data = yaml.safe_load(content)
        except Exception as e:
            raise ValueError(f"Failed to parse CloudFormation template: {e}")

        resources: dict = data.get("Resources", {})
        resource_types = [v.get("Type", "Unknown") for v in resources.values() if isinstance(v, dict)]
        unique_types = list(dict.fromkeys(resource_types))

        lines = [f"CloudFormation template. Resources: {len(resources)} total"]
        for logical_id, res in resources.items():
            if isinstance(res, dict):
                lines.append(f"  {res.get('Type', 'Unknown')}: {logical_id}")

        summary = "\n".join(lines)
        return ParsedInput(
            source_type="iac",
            title="Infrastructure as Code",
            content=summary,
            metadata={
                "format": "cloudformation",
                "resource_count": len(resources),
                "resource_types": unique_types,
            },
        )


    def _parse_terraform(self, content: str) -> ParsedInput:
        try:
            import hcl2
            data = hcl2.loads(content)
        except Exception as e:
            raise ValueError(f"Failed to parse Terraform configuration: {e}")

        # hcl2 returns every block type as a list of dicts
        # resource blocks: [{"aws_s3_bucket": {"data": {...}}}, ...]
        resource_blocks: list = data.get("resource", [])
        resource_type_names: list[str] = []
        instance_count = 0
        for block in (resource_blocks if isinstance(resource_blocks, list) else []):
            for rtype, instances in block.items():
                resource_type_names.append(rtype)
                instance_count += len(instances) if isinstance(instances, dict) else 1

        # providers from required_providers inside terraform {} block
        tf_blocks = data.get("terraform", [])
        providers: list[str] = []
        if tf_blocks:
            rp = tf_blocks[0].get("required_providers", [])
            if rp and isinstance(rp, list) and isinstance(rp[0], dict):
                providers = list(rp[0].keys())
        if not providers:
            seen: set[str] = set()
            for rt in resource_type_names:
                prefix = rt.split("_")[0]
                if prefix not in seen:
                    providers.append(prefix)
                    seen.add(prefix)

        # variables and outputs are also lists of dicts
        variables: list = [k for blk in data.get("variable", []) for k in blk]
        outputs: list = [k for blk in data.get("output", []) for k in blk]

        summary = (
            f"Terraform configuration with providers: {', '.join(providers) or 'unknown'}. "
            f"Resources: {instance_count} instances of {len(resource_type_names)} types. "
            f"Variables: {len(variables)}. Outputs: {len(outputs)}."
        )

        return ParsedInput(
            source_type="iac",
            title="Infrastructure as Code",
            content=summary,
            metadata={
                "format": "terraform",
                "resource_count": instance_count,
                "resource_types": resource_type_names,
            },
        )