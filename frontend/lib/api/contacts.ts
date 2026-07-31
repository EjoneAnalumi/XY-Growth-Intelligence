import { apiRequest } from "@/lib/api/client";
import type { Contact, ContactFormValues } from "@/types/company";

type ContactApiResponse = {
  id: string;
  company_id: string;
  first_name: string;
  last_name: string;
  email: string | null;
  title: string | null;
  role: string | null;
};

type ContactListApiResponse = {
  items: ContactApiResponse[];
  total: number;
};

function mapContact(contact: ContactApiResponse): Contact {
  return {
    id: contact.id,
    companyId: contact.company_id,
    firstName: contact.first_name,
    lastName: contact.last_name,
    email: contact.email ?? "",
    role: contact.title ?? contact.role ?? "",
  };
}

export async function getContacts(): Promise<Contact[]> {
  const response = await apiRequest<ContactListApiResponse>("/contacts");
  return response.items.map(mapContact);
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
