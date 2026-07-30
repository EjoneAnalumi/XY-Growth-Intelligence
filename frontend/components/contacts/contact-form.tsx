"use client";

import { useState } from "react";


type Props = {
  onAdd:(contact:{
    firstName:string;
    lastName:string;
    email:string;
    role:string;
  })=>void;
};


export default function ContactForm({onAdd}:Props){


const [firstName,setFirstName]=useState("");
const [lastName,setLastName]=useState("");
const [email,setEmail]=useState("");
const [role,setRole]=useState("");

const [error,setError] = useState("");
const [success,setSuccess] = useState("");




function handleSubmit(e:React.FormEvent){

e.preventDefault();



const cleanFirstName = firstName.trim();
const cleanLastName = lastName.trim();
const cleanEmail = email.trim();
const cleanRole = role.trim();




if(
  !cleanFirstName ||
  !cleanLastName ||
  !cleanEmail ||
  !cleanRole
){

setError("All fields are required.");
setSuccess("");

return;

}





const nameRegex = /^[a-zA-Z\s]+$/;


if(!nameRegex.test(cleanFirstName)){

setError("First name can contain only letters.");
setSuccess("");

return;

}




if(!nameRegex.test(cleanLastName)){

setError("Last name can contain only letters.");
setSuccess("");

return;

}





const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


if(!emailRegex.test(cleanEmail)){

setError("Please enter a valid email address.");
setSuccess("");

return;

}





if(cleanRole.length < 2){

setError("Role must contain at least 2 characters.");
setSuccess("");

return;

}




setError("");



onAdd({

 firstName:cleanFirstName,

 lastName:cleanLastName,

 email:cleanEmail,

 role:cleanRole

});



setSuccess("Contact added successfully.");



setFirstName("");
setLastName("");
setEmail("");
setRole("");

}





return (

<form 
onSubmit={handleSubmit}
className="rounded-md border bg-card p-6 shadow-sm space-y-4"
>



<h2 className="font-semibold">
Add Contact
</h2>




{error && (

<p className="text-sm text-red-500">
{error}
</p>

)}




{success && (

<p className="text-sm text-green-600">
{success}
</p>

)}






<div className="space-y-3">



<div>

<label className="text-sm font-medium">
First Name
</label>


<input

className="mt-1 border rounded-md p-2 w-full"

placeholder="Enter first name"

value={firstName}

onChange={(e)=>setFirstName(e.target.value)}

/>

</div>





<div>

<label className="text-sm font-medium">
Last Name
</label>


<input

className="mt-1 border rounded-md p-2 w-full"

placeholder="Enter last name"

value={lastName}

onChange={(e)=>setLastName(e.target.value)}

/>

</div>






<div>

<label className="text-sm font-medium">
Email
</label>


<input

className="mt-1 border rounded-md p-2 w-full"

placeholder="Enter email"

type="email"

value={email}

onChange={(e)=>setEmail(e.target.value)}

/>

</div>






<div>

<label className="text-sm font-medium">
Role
</label>


<input

className="mt-1 border rounded-md p-2 w-full"

placeholder="Enter role"

value={role}

onChange={(e)=>setRole(e.target.value)}

/>

</div>



</div>






<button

className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:opacity-90"

>

Add Contact

</button>




</form>

)

}