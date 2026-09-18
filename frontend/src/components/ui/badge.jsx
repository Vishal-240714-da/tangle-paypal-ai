import { forwardRef } from "react";
import { cn } from "@/lib/utils";

const badgeVariants = {
  default:
    "border-transparent bg-primary text-primary-foreground",
  secondary:
    "border-transparent bg-secondary text-secondary-foreground",
  success:
    "border-transparent bg-success/10 text-success",
  warning:
    "border-transparent bg-warning/10 text-warning",
  danger:
    "border-transparent bg-danger/10 text-danger",
  outline:
    "border-border bg-background text-foreground",
};

const Badge = forwardRef(
  ({ className, variant = "default", ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "inline-flex w-fit items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors",
          badgeVariants[variant],
          className
        )}
        {...props}
      />
    );
  }
);

Badge.displayName = "Badge";

export { Badge };