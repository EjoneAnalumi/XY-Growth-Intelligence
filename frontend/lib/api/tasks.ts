import { apiRequest } from "@/lib/api/client";
import type { Task, TaskFormValues } from "@/types/activity-task";

type TaskApiResponse = {
  id: string;
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
};

type TaskListApiResponse = {
  items: TaskApiResponse[];
  total: number;
};

function mapTask(task: TaskApiResponse): Task {
  return {
    id: task.id,
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
  };
}

function buildTaskPayload(values: TaskFormValues) {
  return {
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

export async function completeTask(id: string): Promise<Task> {
  return mapTask(await apiRequest<TaskApiResponse>(`/tasks/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ status: "completed" }),
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
