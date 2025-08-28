import { Skeleton } from './ui/Skeleton';

const MessageSkeleton = () => (
  <div className="flex justify-start mb-3">
    <div className="flex items-start gap-2">
      <Skeleton className="w-6 h-6 rounded-full" />
      <div className="flex-1">
        <Skeleton className="h-4 w-32 mb-2" />
        <Skeleton className="h-3 w-24" />
      </div>
    </div>
  </div>
);

export default MessageSkeleton;