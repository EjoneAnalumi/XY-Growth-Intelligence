type Props = {
  firstName: string;
  lastName: string;
  email: string;
  role: string;
};


export default function ContactCard({
  firstName,
  lastName,
  email,
  role,
}: Props) {


  return (
    <div className="rounded-md border bg-card p-4 shadow-sm">

      <h3 className="font-semibold">
        {firstName} {lastName}
      </h3>


      <p className="text-sm text-muted-foreground">
        {email}
      </p>


      <p className="mt-1 text-sm">
        Role: {role}
      </p>


    </div>
  );
}