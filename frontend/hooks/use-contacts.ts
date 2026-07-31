"use client";

import { useEffect, useState } from "react";

import { contacts as mockContacts } from "@/lib/mock/contacts";
import type { Contact } from "@/types/company";

export function useContacts() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      setTimeout(() => {
        setContacts(mockContacts);
        setLoading(false);
      }, 1000);
    } catch {
      setError("Failed to load contacts");
      setLoading(false);
    }
  }, []);

  return {
    contacts,
    loading,
    error,
    setContacts,
  };
}
