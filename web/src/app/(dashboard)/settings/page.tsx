"use client";
import { useUser } from "@clerk/nextjs";

export default function SettingsPage() {
  const { user } = useUser();

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold mb-6">Settings</h1>

      <div className="border border-gray-800 rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Profile</h2>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-400">Email</span>
            <span>{user?.primaryEmailAddress?.emailAddress || "—"}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">User ID</span>
            <span className="font-mono text-xs">{user?.id || "—"}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
