export type Contact = {
  id: string;
  companyId: string;
  firstName: string;
  lastName: string;
  email: string;
  role: string;
};


export const contacts: Contact[] = [
  {
    id: "1",
    companyId: "1",
    firstName: "John",
    lastName: "Smith",
    email: "john@xy-cyber.com",
    role: "CEO",
  },
  {
    id: "2",
    companyId: "2",
    firstName: "Anna",
    lastName: "Brown",
    email: "anna@abcfinance.com",
    role: "Manager",
  },
  {
    id: "3",
    companyId: "3",
    firstName: "David",
    lastName: "Wilson",
    email: "david@techcorp.com",
    role: "Security Analyst",
  },
];