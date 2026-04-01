import { IntakeWizard } from '@/components/idea/IntakeWizard';

export const metadata = {
  title: 'Idea Mode — ARCHON',
  description: 'Describe your product idea and get three architecture options from 6 specialist AI architects.',
};

export default function IdeaPage() {
  return <IntakeWizard />;
}
