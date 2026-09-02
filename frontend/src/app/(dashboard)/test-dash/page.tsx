'use client';

export default function TestDashboard() {
  return (
    <div className="p-8 bg-white dark:bg-gray-900 min-h-screen">
      <h1 className="text-4xl font-bold text-black dark:text-white mb-4">
        TEST DASHBOARD - THIS SHOULD BE VISIBLE
      </h1>
      <div className="bg-red-500 text-white p-4 rounded-lg mb-4">
        <p className="font-bold">If you can see this red box, CSS is loading!</p>
      </div>
      <div className="bg-green-500 text-white p-4 rounded-lg mb-4">
        <p className="font-bold">If you can see this green box, Tailwind is working!</p>
      </div>
      <div className="bg-blue-500 text-white p-4 rounded-lg">
        <p className="font-bold">If you can see this blue box, the page is rendering!</p>
      </div>
      <div className="mt-8 space-y-2">
        <p className="text-gray-800 dark:text-gray-200">Current theme should be visible above</p>
        <p className="text-gray-800 dark:text-gray-200">Check browser console (F12) for any errors</p>
        <p className="text-gray-800 dark:text-gray-200">Navigate to: http://localhost:3000/test-dash</p>
      </div>
    </div>
  );
}
