import { Skeleton } from "@/components/ui/skeleton";

export const AnalyticsSkeleton = () => {
  return (
    <div className="p-8 space-y-6">
      <div className="mb-6">
        <Skeleton data-testid="skeleton-element" className="h-9 w-48 mb-2" />
        <Skeleton data-testid="skeleton-element" className="h-5 w-80" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-6 gap-4 auto-rows-fr">
        <div className="md:col-span-2 p-6 bg-white rounded-lg shadow-md border border-gray-100 space-y-2">
          <Skeleton data-testid="skeleton-element" className="h-4 w-24" />
          <Skeleton data-testid="skeleton-element" className="h-9 w-16" />
        </div>
        <div className="md:col-span-2 p-6 bg-white rounded-lg shadow-md border border-gray-100 space-y-2">
          <Skeleton data-testid="skeleton-element" className="h-4 w-24" />
          <Skeleton data-testid="skeleton-element" className="h-9 w-16" />
        </div>
        <div className="md:col-span-2 md:row-span-2 p-6 bg-white rounded-lg shadow-md border border-gray-100">
          <div className="flex justify-between items-center mb-4">
            <Skeleton data-testid="skeleton-element" className="h-6 w-24" />
            <Skeleton data-testid="skeleton-element" className="h-8 w-20" />
          </div>
          <Skeleton
            data-testid="skeleton-element"
            className="h-[200px] w-full"
          />
        </div>
        <div className="md:col-span-2 p-6 bg-white rounded-lg shadow-md border border-gray-100 space-y-2">
          <Skeleton data-testid="skeleton-element" className="h-4 w-24" />
          <Skeleton data-testid="skeleton-element" className="h-9 w-16" />
        </div>
        <div className="md:col-span-2 p-6 bg-white rounded-lg shadow-md border border-gray-100 space-y-2">
          <Skeleton data-testid="skeleton-element" className="h-4 w-24" />
          <Skeleton data-testid="skeleton-element" className="h-9 w-16" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100">
          <Skeleton data-testid="skeleton-element" className="h-6 w-32 mb-4" />
          <Skeleton
            data-testid="skeleton-element"
            className="h-[300px] w-full"
          />
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100">
          <Skeleton data-testid="skeleton-element" className="h-6 w-32 mb-4" />
          <Skeleton
            data-testid="skeleton-element"
            className="h-[300px] w-full"
          />
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100 space-y-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <Skeleton data-testid="skeleton-element" className="h-6 w-44" />
          <Skeleton data-testid="skeleton-element" className="h-9 w-40" />
        </div>
        <Skeleton data-testid="skeleton-element" className="h-20 w-full" />
        <Skeleton data-testid="skeleton-element" className="h-20 w-full" />
        <Skeleton data-testid="skeleton-element" className="h-20 w-full" />
      </div>
    </div>
  );
};
