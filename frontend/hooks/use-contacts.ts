"use client";

import { useEffect, useState } from "react";
import { contacts as mockContacts, Contact } from "@/lib/mock/contacts";


export function useContacts() {

  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {

    try {

      setTimeout(() => {

        setContacts(mockContacts);
        setLoading(false);

      },1000);


    } catch {

      setError("Failed to load contacts");
      setLoading(false);

    }

  }, []);


  return {
    contacts,
    loading,
    error,
    setContacts
  };

}