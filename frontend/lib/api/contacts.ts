import { apiRequest } from "@/lib/api/client";
import { allPages } from "@/lib/api/pagination";
import type { Contact, ContactFormValues } from "@/types/company";

type ContactApiResponse = {
  id: string;
  created_at?: string;
  company_id: string;
  first_name: string;
  last_name: string;
  email: string | null;
  title: string | null;
  role: string | null;
};


function mapContact(contact: ContactApiResponse): Contact {
  return {
    id: contact.id,
    createdAt: contact.created_at ?? "",
    companyId: contact.company_id,
    firstName: contact.first_name,
    lastName: contact.last_name,
    email: contact.email ?? "",
    role: contact.title ?? contact.role ?? "",
  };
}

export async function getContacts(): Promise<Contact[]> {
  return (await allPages<ContactApiResponse>("/contacts")).map(mapContact);
}

export async function createContact(payload: ContactFormValues): Promise<Contact> {
  const response = await apiRequest<ContactApiResponse>("/contacts", {
    method: "POST",
    body: JSON.stringify({
      company_id: payload.companyId,
      first_name: payload.firstName,
      last_name: payload.lastName,
      email: payload.email,
      title: payload.role,
      decision_category: "unknown",
    }),
  });

  return mapContact(response);
}

export async function updateContact(id: string, payload: ContactFormValues): Promise<Contact> {
  const response = await apiRequest<ContactApiResponse>(`/contacts/${id}`, {
    method: "PATCH",
    body: JSON.stringify({
      company_id: payload.companyId,
      first_name: payload.firstName,
      last_name: payload.lastName,
      email: payload.email,
      title: payload.role,
    }),
  });
  return mapContact(response);
}

export async function archiveContact(id: string): Promise<void> {
  await apiRequest(`/contacts/${id}`, { method: "DELETE" });
}
