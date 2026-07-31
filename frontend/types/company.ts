export type Company = {
  id: string;
  name: string;
  domain: string;
  industry: string;
  country: string;
  status?: string;
};

export type CompanyFormValues = {
  name: string;
  domain: string;
  industry: string;
  country: string;
};

export type Contact = {
  id: string;
  companyId: string;
  firstName: string;
  lastName: string;
  email: string;
  role: string;
};

export type ContactFormValues = {
  companyId: string;
  firstName: string;
  lastName: string;
  email: string;
  role: string;
};
