"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";

const NAV_ITEMS = [
  { href: "/reviews", label: "Reviews", icon: "📋" },
  { href: "/reviews/new", label: "New Review", icon: "➕" },
  { href: "/billing", label: "Billing", icon: "💳" },
  { href: "/settings", label: "Settings", icon: "⚙️" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-64 border-r border-gray-200 bg-white">
        <div className="flex h-16 items-center border-b px-6">
          <Link href="/" className="text-xl font-bold text-archon-700">ARCHON</Link>
        </div>
        <nav className="mt-4 space-y-1 px-3">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                pathname === item.href
                  ? "bg-archon-50 text-archon-700"
                  : "text-gray-600 hover:bg-gray-100"
              )}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-5xl px-8 py-8">
          {children}
        </div>
      </main>
    </div>
  );
}
