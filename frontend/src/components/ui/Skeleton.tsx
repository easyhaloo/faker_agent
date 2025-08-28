interface SkeletonProps {
  className?: string;
}

export const Skeleton = ({ className = '' }: SkeletonProps) => {
  return (
    <div className={`bg-muted animate-pulse rounded ${className}`} />
  );
};