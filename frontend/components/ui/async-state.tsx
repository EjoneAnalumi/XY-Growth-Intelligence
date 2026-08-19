import { AlertCircle, Inbox, LoaderCircle } from "lucide-react";
import { HTMLAttributes, ReactNode } from "react";

import { Button } from "@/components/ui/button";

type StateProps = {
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
};

function StateContainer({
  children,
  className = "",
  ...props
}: { children: ReactNode; className?: string } & HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`flex min-h-32 flex-col items-center justify-center rounded-md border bg-card px-4 py-6 text-center ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export function LoadingState({ title = "Loading", className }: Pick<StateProps, "title" | "className">) {
  return (
    <StateContainer className={className} role="status" aria-live="polite">
      <LoaderCircle className="size-6 animate-spin text-primary" aria-hidden="true" />
      <p className="mt-3 text-sm text-muted-foreground">{title}</p>
    </StateContainer>
  );
}

export function EmptyState({ title, description, action, className }: StateProps) {
  return (
    <StateContainer className={className}>
      <Inbox className="size-6 text-muted-foreground" aria-hidden="true" />
      <h3 className="mt-3 text-sm font-semibold">{title}</h3>
      {description ? <p className="mt-1 max-w-md text-sm text-muted-foreground">{description}</p> : null}
      {action ? <div className="mt-4">{action}</div> : null}
    </StateContainer>
  );
}

type ErrorStateProps = StateProps & {
  onRetry?: () => void;
  retryLabel?: string;
};

export function ErrorState({
  title,
  description,
  onRetry,
  retryLabel = "Try again",
  className,
}: ErrorStateProps) {
  return (
    <StateContainer className={className} role="alert">
      <AlertCircle className="size-6 text-destructive" aria-hidden="true" />
      <h3 className="mt-3 text-sm font-semibold text-destructive">{title}</h3>
      {description ? <p className="mt-1 max-w-md text-sm text-muted-foreground">{description}</p> : null}
      {onRetry ? (
        <Button type="button" variant="outline" className="mt-4" onClick={onRetry}>
          {retryLabel}
        </Button>
      ) : null}
    </StateContainer>
  );
}
