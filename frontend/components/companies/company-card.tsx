type CompanyCardProps = {
  name: string;
  domain: string;
  industry: string;
  country: string;
};

export default function CompanyCard({
  name,
  domain,
  industry,
  country,
}: CompanyCardProps) {
  return (
    <div className="border rounded-lg p-4 mb-4 bg-white shadow-sm">
      <h2 className="text-lg font-semibold">{name}</h2>

      <p>{domain}</p>

      <p>{industry}</p>

      <p>{country}</p>

      <div className="mt-4 flex gap-2">
        <button className="px-3 py-1 bg-blue-600 text-white rounded">
          View
        </button>

        <button className="px-3 py-1 bg-gray-200 rounded">
          Edit
        </button>
      </div>
    </div>
  );
}