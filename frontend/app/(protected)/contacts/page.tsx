"use client";

import { useState } from "react";
import { Users } from "lucide-react";

import ContactCard from "@/components/contacts/contact-card";
import ContactForm from "@/components/contacts/contact-form";
import { useContacts } from "@/hooks/use-contacts";


type Contact = {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  role: string;
  companyId: string;
};



export default function ContactsPage() {


  const {
    contacts,
    loading,
    error,
  } = useContacts();



  const [showForm, setShowForm] = useState(false);



  const [contactList, setContactList] = useState<Contact[]>([]);





  function handleAdd(contact:{
    firstName:string;
    lastName:string;
    email:string;
    role:string;
  }) {


    const newContact: Contact = {

      id: crypto.randomUUID(),

      companyId:"1",

      ...contact

    };



    setContactList((prev)=>[
      ...prev,
      newContact
    ]);



    setShowForm(false);

  }





  const allContacts = [
    ...contacts,
    ...contactList,
  ];






  return (

    <div className="space-y-5">



      {/* Header */}

      <div>


        <p className="text-sm font-medium text-primary">
          CRM
        </p>



        <div className="mt-1 flex items-center justify-between">



          <div>


            <h1 className="text-2xl font-semibold tracking-normal sm:text-3xl">
              Contacts
            </h1>



            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
              Manage company contacts and relationships.
            </p>


          </div>





          <button

            onClick={() => setShowForm((prev)=>!prev)}

            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:opacity-90"

          >

            + Add Contact

          </button>



        </div>


      </div>








      {/* Add Contact Form */}


      {showForm && (

        <ContactForm
          onAdd={handleAdd}
        />

      )}









      {/* Contact List */}



      <section className="rounded-md border bg-card p-6 shadow-sm">





        <div className="mb-6 flex items-center gap-3">


          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-muted">


            <Users className="h-5 w-5 text-primary" />


          </div>





          <div>


            <h2 className="font-semibold">
              Contact List
            </h2>



            <p className="text-sm text-muted-foreground">
              Contacts loaded from mock API.
            </p>


          </div>



        </div>








        {/* Loading */}


        {loading && (

          <p className="text-sm text-muted-foreground">
            Loading contacts...
          </p>

        )}








        {/* Error */}


        {error && (

          <p className="text-sm text-red-500">
            Failed to load contacts. Please try again.
          </p>

        )}








        {/* Empty */}


        {!loading && !error && allContacts.length === 0 && (

          <p className="text-sm text-muted-foreground">
            No contacts found.
          </p>

        )}









        {/* Data */}


        {!loading && !error && allContacts.length > 0 && (

          <div className="space-y-4">


            {allContacts.map((contact)=>(


              <ContactCard

                key={contact.id}

                firstName={contact.firstName}

                lastName={contact.lastName}

                email={contact.email}

                role={contact.role}

              />


            ))}



          </div>

        )}






      </section>





    </div>

  );

}