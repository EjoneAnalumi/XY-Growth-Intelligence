export type ActivityType =
  | "call"
  | "email"
  | "meeting"
  | "linkedin_message"
  | "conference"
  | "introduction"
  | "workshop"
  | "demo"
  | "proposal"
  | "follow_up"
  | "internal_note";

export type Activity = {
  id: string;
  companyId: string;
  contactId: string | null;
  opportunityId: string | null;
  activityType: ActivityType;
  subject: string;
  notes: string;
  occurredAt: string;
  archivedAt: string | null;
  createdAt: string;
  updatedAt: string;
  createdBy: string | null;
  updatedBy: string | null;
};

export type ActivityFormValues = {
  companyId: string;
  contactId: string;
  opportunityId: string;
  activityType: ActivityType;
  subject: string;
  notes: string;
  occurredAt: string;
};

export type TaskPriority = "low" | "medium" | "high" | "urgent";
export type TaskStatus = "open" | "in_progress" | "completed" | "cancelled";

export type Task = {
  id: string;
  companyId: string | null;
  opportunityId: string | null;
  title: string;
  description: string;
  dueAt: string;
  priority: TaskPriority;
  status: TaskStatus;
  outcome: string;
  completedAt: string | null;
  archivedAt: string | null;
  createdAt: string;
  updatedAt: string;
  createdBy: string | null;
  updatedBy: string | null;
};

export type TaskFormValues = {
  companyId: string;
  opportunityId: string;
  title: string;
  description: string;
  dueAt: string;
  priority: TaskPriority;
  status: TaskStatus;
};
