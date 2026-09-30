import { apiRequest } from "@/lib/api/client";
import type { Task, TaskFormValues } from "@/types/activity-task";

type TaskApiResponse = {
  assigned_by: string | null;
  assigned_at: string | null;
  id: string;
  owner_id: string | null;
  company_id: string | null;
  opportunity_id: string | null;
  title: string;
  description: string | null;
  due_at: string | null;
  priority: Task["priority"];
  status: Task["status"];
  outcome: string | null;
  completed_at: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
  created_by: string | null;
  updated_by: string | null;
};

type TaskListApiResponse = {
  items: TaskApiResponse[];
  total: number;
};

function mapTask(task: TaskApiResponse): Task {
  return {
    id: task.id,
    assignedBy: task.assigned_by,
    assignedAt: task.assigned_at,
    ownerId: task.owner_id,
    companyId: task.company_id,
    opportunityId: task.opportunity_id,
    title: task.title,
    description: task.description ?? "",
    dueAt: task.due_at ?? "",
    priority: task.priority,
    status: task.status,
    outcome: task.outcome ?? "",
    completedAt: task.completed_at,
    archivedAt: task.archived_at,
    createdAt: task.created_at,
    updatedAt: task.updated_at,
    createdBy: task.created_by,
    updatedBy: task.updated_by,
  };
}

function buildTaskPayload(values: TaskFormValues) {
  return {
    owner_id: values.ownerId === "unassigned" ? null : values.ownerId || undefined,
    company_id: values.companyId || null,
    opportunity_id: values.opportunityId || null,
    title: values.title,
    description: values.description || null,
    due_at: values.dueAt || null,
    priority: values.priority,
    status: values.status,
  };
}

export async function getTasks(): Promise<Task[]> {
  const response = await apiRequest<TaskListApiResponse>("/tasks");
  return response.items.map(mapTask);
}

export async function createTask(values: TaskFormValues): Promise<Task> {
  const response = await apiRequest<TaskApiResponse>("/tasks", {
    method: "POST",
    body: JSON.stringify(buildTaskPayload(values)),
  });

  return mapTask(response);
}

export async function completeTask(id: string, outcome = ""): Promise<Task> {
  return mapTask(await apiRequest<TaskApiResponse>(`/tasks/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ status: "completed", outcome }),
  }));
}

export async function updateTask(id: string, values: { title: string; description: string }): Promise<Task> {
  return mapTask(await apiRequest<TaskApiResponse>(`/tasks/${id}`, {
    method: "PATCH",
    body: JSON.stringify(values),
  }));
}

export async function archiveTask(id: string): Promise<void> {
  await apiRequest(`/tasks/${id}`, { method: "DELETE" });
}
