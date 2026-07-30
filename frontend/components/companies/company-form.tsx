"use client";

import { useState } from "react";


type CompanyFormProps = {
  onAdd: (company: {
    name: string;
    domain: string;
    industry: string;
    country: string;
  }) => void;
};


export default function CompanyForm({
  onAdd,
}: CompanyFormProps) {


  const [name, setName] = useState("");
  const [domain, setDomain] = useState("");
  const [industry, setIndustry] = useState("");
  const [country, setCountry] = useState("");

  const [error, setError] = useState("");



  function handleSubmit(e: React.FormEvent) {

    e.preventDefault();


    // validation

const domainRegex = /^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$/;


if (!name || !domain || !industry || !country) {

  setError("All fields are required");
  return;

}


if (!domainRegex.test(domain)) {

  setError("Please enter a valid domain (example.com)");
  return;

}


if (name.length < 2) {

  setError("Company name is too short");
  return;

}


    setError("");



    onAdd({
      name,
      domain,
      industry,
      country,
    });



    setName("");
    setDomain("");
    setIndustry("");
    setCountry("");

  }



  return (

    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-md border bg-card p-5"
    >


      <h2 className="font-semibold">
        Add Company
      </h2>



      {error && (

        <p className="text-sm text-red-500">
          {error}
        </p>

      )}



      <input
        className="w-full rounded-md border p-2"
        placeholder="Company name"
        value={name}
        onChange={(e)=>setName(e.target.value)}
      />



      <input
        className="w-full rounded-md border p-2"
        placeholder="Domain"
        value={domain}
        onChange={(e)=>setDomain(e.target.value)}
      />



      <input
        className="w-full rounded-md border p-2"
        placeholder="Industry"
        value={industry}
        onChange={(e)=>setIndustry(e.target.value)}
      />



      <input
        className="w-full rounded-md border p-2"
        placeholder="Country"
        value={country}
        onChange={(e)=>setCountry(e.target.value)}
      />



      <button
        className="rounded-md bg-primary px-4 py-2 text-white"
      >
        Save Company
      </button>


    </form>

  );

}