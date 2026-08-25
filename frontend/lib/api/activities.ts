import { apiRequest } from "@/lib/api/client";
import type { Activity, ActivityFormValues } from "@/types/activity-task";

type ActivityApiResponse = {
  id: string;
  company_id: string;
  contact_id: string | null;
  opportunity_id: string | null;
  activity_type: Activity["activityType"];
  subject: string;
  notes: string | null;
  occurred_at: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
  created_by: string | null;
  updated_by: string | null;
};

type ActivityListApiResponse = {
  items: ActivityApiResponse[];
  total: number;
};

function mapActivity(activity: ActivityApiResponse): Activity {
  return {
    id: activity.id,
    companyId: activity.company_id,
    contactId: activity.contact_id,
    opportunityId: activity.opportunity_id,
    activityType: activity.activity_type,
    subject: activity.subject,
    notes: activity.notes ?? "",
    occurredAt: activity.occurred_at ?? "",
    archivedAt: activity.archived_at,
    createdAt: activity.created_at,
    updatedAt: activity.updated_at,
    createdBy: activity.created_by,
    updatedBy: activity.updated_by,
  };
}

function buildActivityPayload(values: ActivityFormValues) {
  return {
    company_id: values.companyId,
    contact_id: values.contactId || null,
    opportunity_id: values.opportunityId || null,
    activity_type: values.activityType,
    subject: values.subject,
    notes: values.notes || null,
    occurred_at: values.occurredAt || null,
  };
}

export async function getActivities(): Promise<Activity[]> {
  const response = await apiRequest<ActivityListApiResponse>("/activities");
  return response.items.map(mapActivity);
}

export async function createActivity(values: ActivityFormValues): Promise<Activity> {
  const response = await apiRequest<ActivityApiResponse>("/activities", {
    method: "POST",
    body: JSON.stringify(buildActivityPayload(values)),
  });

  return mapActivity(response);
}

export async function updateActivity(
  id: string,
  values: Pick<ActivityFormValues, "subject" | "notes">,
): Promise<Activity> {
  return mapActivity(await apiRequest<ActivityApiResponse>(`/activities/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ subject: values.subject, notes: values.notes || null }),
  }));
}

export async function archiveActivity(id: string): Promise<void> {
  await apiRequest(`/activities/${id}`, { method: "DELETE" });
}
