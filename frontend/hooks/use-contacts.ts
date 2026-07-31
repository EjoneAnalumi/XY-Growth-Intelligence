"use client";

import { useEffect, useState } from "react";

import { getContacts } from "@/lib/api/contacts";
import type { Contact } from "@/types/company";

export function useContacts() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refreshContacts() {
    try {
      setLoading(true);
      setError(null);
      const data = await getContacts();
      setContacts(data);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to load contacts");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshContacts();
  }, []);

  return {
    contacts,
    loading,
    error,
    setContacts,
    refreshContacts,
  };
}
