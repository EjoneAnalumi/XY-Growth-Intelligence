"use client";

import { CalendarPlus, MessageSquarePlus } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createActivity, getActivities } from "@/lib/api/activities";
import { createTask, getTasks } from "@/lib/api/tasks";
import type {
  Activity,
  ActivityFormValues,
  ActivityType,
  Task,
  TaskFormValues,
  TaskPriority,
} from "@/types/activity-task";
import type { Company, Contact } from "@/types/company";
import type { Opportunity } from "@/types/opportunity";

type ActivityTaskPanelProps = {
  opportunity: Opportunity;
  companies: Company[];
  contacts: Contact[];
};

const activityTypes: { value: ActivityType; label: string }[] = [
  { value: "call", label: "Call" },
  { value: "email", label: "Email" },
  { value: "meeting", label: "Meeting" },
  { value: "linkedin_message", label: "LinkedIn Message" },
  { value: "conference", label: "Conference" },
  { value: "introduction", label: "Introduction" },
  { value: "workshop", label: "Workshop" },
  { value: "demo", label: "Demo" },
  { value: "proposal", label: "Proposal" },
  { value: "follow_up", label: "Follow-up" },
  { value: "internal_note", label: "Internal Note" },
];

const taskPriorities: TaskPriority[] = ["low", "medium", "high", "urgent"];

export default function ActivityTaskPanel({
  opportunity,
  companies,
  contacts,
}: ActivityTaskPanelProps) {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activityError, setActivityError] = useState<string | null>(null);
  const [taskError, setTaskError] = useState<string | null>(null);
  const [isSavingActivity, setIsSavingActivity] = useState(false);
  const [isSavingTask, setIsSavingTask] = useState(false);
  const [activityValues, setActivityValues] = useState<ActivityFormValues>({
    companyId: opportunity.companyId,
    contactId: opportunity.contactId ?? "",
    opportunityId: opportunity.id,
    activityType: "meeting",
    subject: "",
    notes: "",
    occurredAt: "",
  });
  const [taskValues, setTaskValues] = useState<TaskFormValues>({
    companyId: opportunity.companyId,
    opportunityId: opportunity.id,
    title: opportunity.nextAction || "",
    description: "",
    dueAt: opportunity.nextActionDueAt ? opportunity.nextActionDueAt.slice(0, 16) : "",
    priority: "medium",
    status: "open",
  });

  useEffect(() => {
    async function loadRecords() {
      try {
        setLoading(true);
        setError(null);
        const [activityResponse, taskResponse] = await Promise.all([getActivities(), getTasks()]);
        setActivities(
          activityResponse.filter((activity) => activity.opportunityId === opportunity.id),
        );
        setTasks(taskResponse.filter((task) => task.opportunityId === opportunity.id));
      } catch (caughtError) {
        setError(caughtError instanceof Error ? caughtError.message : "Failed to load follow-up work.");
      } finally {
        setLoading(false);
      }
    }

    loadRecords();
  }, [opportunity.id]);

  const companyName = useMemo(
    () =>
      companies.find((company) => company.id === opportunity.companyId)?.name ?? "Unknown company",
    [companies, opportunity.companyId],
  );
  const contactName = useMemo(() => {
    const contact = contacts.find((item) => item.id === opportunity.contactId);
    return contact ? `${contact.firstName} ${contact.lastName}` : "No primary contact";
  }, [contacts, opportunity.contactId]);

  async function handleActivitySubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!activityValues.subject.trim()) {
      setActivityError("Activity subject is required.");
      return;
    }

    try {
      setIsSavingActivity(true);
      setActivityError(null);
      const created = await createActivity({
        ...activityValues,
        subject: activityValues.subject.trim(),
        notes: activityValues.notes.trim(),
      });
      setActivities((current) => [created, ...current]);
      setActivityValues((current) => ({ ...current, subject: "", notes: "", occurredAt: "" }));
    } catch (caughtError) {
      setActivityError(
        caughtError instanceof Error ? caughtError.message : "Failed to create activity.",
      );
    } finally {
      setIsSavingActivity(false);
    }
  }

  async function handleTaskSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!taskValues.title.trim()) {
      setTaskError("Task title is required.");
      return;
    }

    try {
      setIsSavingTask(true);
      setTaskError(null);
      const created = await createTask({
        ...taskValues,
        title: taskValues.title.trim(),
        description: taskValues.description.trim(),
      });
      setTasks((current) => [created, ...current]);
      setTaskValues((current) => ({ ...current, title: "", description: "", dueAt: "" }));
    } catch (caughtError) {
      setTaskError(caughtError instanceof Error ? caughtError.message : "Failed to create task.");
    } finally {
      setIsSavingTask(false);
    }
  }

  return (
    <section className="rounded-md border bg-card p-5 shadow-sm">
      <div>
        <h2 className="font-semibold">Activities and Tasks</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Record work against {companyName} and schedule the next follow-up for {contactName}.
        </p>
      </div>

      {error ? (
        <p className="mt-4 rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </p>
      ) : null}

      <div className="mt-5 grid gap-5 xl:grid-cols-2">
        <form onSubmit={handleActivitySubmit} className="space-y-4 rounded-md border bg-background p-4">
          <div className="flex items-center gap-3">
            <MessageSquarePlus className="h-5 w-5 text-primary" />
            <h3 className="text-sm font-semibold">New Activity</h3>
          </div>

          {activityError ? <p className="text-sm text-destructive">{activityError}</p> : null}

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="activity-type">Type</Label>
              <select
                id="activity-type"
                className="h-10 w-full rounded-md border bg-background px-3 text-sm"
                value={activityValues.activityType}
                onChange={(event) =>
                  setActivityValues((current) => ({
                    ...current,
                    activityType: event.target.value as ActivityType,
                  }))
                }
              >
                {activityTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="activity-occurred">Occurred</Label>
              <Input
                id="activity-occurred"
                type="datetime-local"
                value={activityValues.occurredAt}
                onChange={(event) =>
                  setActivityValues((current) => ({ ...current, occurredAt: event.target.value }))
                }
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="activity-subject">Subject</Label>
            <Input
              id="activity-subject"
              value={activityValues.subject}
              onChange={(event) =>
                setActivityValues((current) => ({ ...current, subject: event.target.value }))
              }
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="activity-notes">Notes</Label>
            <textarea
              id="activity-notes"
              className="min-h-24 w-full rounded-md border bg-background px-3 py-2 text-sm"
              value={activityValues.notes}
              onChange={(event) =>
                setActivityValues((current) => ({ ...current, notes: event.target.value }))
              }
            />
          </div>

          <Button type="submit" disabled={isSavingActivity} className="gap-2">
            <MessageSquarePlus className="h-4 w-4" />
            {isSavingActivity ? "Recording..." : "Record activity"}
          </Button>
        </form>

        <form onSubmit={handleTaskSubmit} className="space-y-4 rounded-md border bg-background p-4">
          <div className="flex items-center gap-3">
            <CalendarPlus className="h-5 w-5 text-primary" />
            <h3 className="text-sm font-semibold">New Task</h3>
          </div>

          {taskError ? <p className="text-sm text-destructive">{taskError}</p> : null}

          <div className="space-y-2">
            <Label htmlFor="task-title">Title</Label>
            <Input
              id="task-title"
              value={taskValues.title}
              onChange={(event) =>
                setTaskValues((current) => ({ ...current, title: event.target.value }))
              }
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="task-due">Due</Label>
              <Input
                id="task-due"
                type="datetime-local"
                value={taskValues.dueAt}
                onChange={(event) =>
                  setTaskValues((current) => ({ ...current, dueAt: event.target.value }))
                }
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="task-priority">Priority</Label>
              <select
                id="task-priority"
                className="h-10 w-full rounded-md border bg-background px-3 text-sm"
                value={taskValues.priority}
                onChange={(event) =>
                  setTaskValues((current) => ({
                    ...current,
                    priority: event.target.value as TaskPriority,
                  }))
                }
              >
                {taskPriorities.map((priority) => (
                  <option key={priority} value={priority}>
                    {priority}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="task-description">Description</Label>
            <textarea
              id="task-description"
              className="min-h-24 w-full rounded-md border bg-background px-3 py-2 text-sm"
              value={taskValues.description}
              onChange={(event) =>
                setTaskValues((current) => ({ ...current, description: event.target.value }))
              }
            />
          </div>

          <Button type="submit" disabled={isSavingTask} className="gap-2">
            <CalendarPlus className="h-4 w-4" />
            {isSavingTask ? "Scheduling..." : "Schedule task"}
          </Button>
        </form>
      </div>

      <div className="mt-5 grid gap-4 xl:grid-cols-2">
        <div className="rounded-md border bg-background p-4">
          <h3 className="text-sm font-semibold">Recent Activities</h3>
          {loading ? <p className="mt-3 text-sm text-muted-foreground">Loading activities...</p> : null}
          {!loading && activities.length === 0 ? (
            <p className="mt-3 text-sm text-muted-foreground">No activities recorded yet.</p>
          ) : null}
          <div className="mt-3 space-y-3">
            {activities.map((activity) => (
              <div key={activity.id} className="rounded-md border px-3 py-2 text-sm">
                <p className="font-medium">{activity.subject}</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {activity.activityType.replaceAll("_", " ")}{" "}
                  {activity.occurredAt ? `- ${activity.occurredAt}` : ""}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-md border bg-background p-4">
          <h3 className="text-sm font-semibold">Open Tasks</h3>
          {loading ? <p className="mt-3 text-sm text-muted-foreground">Loading tasks...</p> : null}
          {!loading && tasks.length === 0 ? (
            <p className="mt-3 text-sm text-muted-foreground">No tasks scheduled yet.</p>
          ) : null}
          <div className="mt-3 space-y-3">
            {tasks.map((task) => (
              <div key={task.id} className="rounded-md border px-3 py-2 text-sm">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium">{task.title}</p>
                  <span className="rounded-md bg-muted px-2 py-1 text-xs text-muted-foreground">
                    {task.priority}
                  </span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  {task.status} {task.dueAt ? `- due ${task.dueAt}` : ""}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
