"use client";

import { useState } from "react";
import { Building2 } from "lucide-react";

import CompanyCard from "@/components/companies/company-card";
import CompanyForm from "@/components/companies/company-form";
import { useCompanies } from "@/hooks/use-companies";


type Company = {
  id: string;
  name: string;
  domain: string;
  industry: string;
  country: string;
};



export default function CompaniesPage() {


  const {
    companies,
    loading,
    error,
  } = useCompanies();



  const [showForm, setShowForm] = useState(false);



  const [companyList, setCompanyList] = useState<Company[]>([]);




  function handleAdd(company: {
    name: string;
    domain: string;
    industry: string;
    country: string;
  }) {


    const newCompany: Company = {
      id: crypto.randomUUID(),
      ...company,
    };


    setCompanyList((prev) => [
      ...prev,
      newCompany,
    ]);


    setShowForm(false);

  }




  const allCompanies = [
    ...companies,
    ...companyList,
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
              Companies
            </h1>



            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
              Manage companies, view details, and prepare for backend integration.
            </p>


          </div>





          <button

            onClick={() => setShowForm((prev) => !prev)}

            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:opacity-90"

          >

            + Add Company

          </button>



        </div>


      </div>





      {/* Add Company Form */}


      {showForm && (

        <CompanyForm
          onAdd={handleAdd}
        />

      )}







      {/* Company List */}


      <section className="rounded-md border bg-card p-6 shadow-sm">


        <div className="mb-6 flex items-center gap-3">


          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-muted">


            <Building2 className="h-5 w-5 text-primary" />


          </div>




          <div>


            <h2 className="font-semibold">
              Company List
            </h2>



            <p className="text-sm text-muted-foreground">
              Companies loaded from mock API.
            </p>


          </div>


        </div>







        {/* Loading */}

        {loading && (

          <p className="text-sm text-muted-foreground">
            Loading companies...
          </p>

        )}







        {/* Error */}

        {error && (

          <p className="text-sm text-red-500">
            Failed to load companies. Please try again.
          </p>

        )}








        {/* Empty */}

        {!loading && !error && allCompanies.length === 0 && (

          <p className="text-sm text-muted-foreground">
            No companies found.
          </p>

        )}









        {/* Data */}

        {!loading && !error && allCompanies.length > 0 && (

          <div className="space-y-4">


            {allCompanies.map((company) => (

              <CompanyCard

                key={company.id}

                name={company.name}

                domain={company.domain}

                industry={company.industry}

                country={company.country}

              />

            ))}


          </div>

        )}





      </section>


    </div>

  );

}