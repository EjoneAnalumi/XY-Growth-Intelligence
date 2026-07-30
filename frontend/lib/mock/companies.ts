export type Company = {
  id: string;
  name: string;
  domain: string;
  industry: string;
  country: string;
};

export const companies: Company[] = [
  {
    id: "1",
    name: "XY Cyber",
    domain: "xy-cyber.com",
    industry: "Cyber Security",
    country: "Kosovo",
  },
  {
    id: "2",
    name: "ABC Finance",
    domain: "abcfinance.com",
    industry: "Finance",
    country: "Germany",
  },
  {
    id: "3",
    name: "Tech Solutions",
    domain: "techsolutions.com",
    industry: "Technology",
    country: "Switzerland",
  },
];