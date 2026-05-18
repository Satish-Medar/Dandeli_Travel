/* Sign-up page for new users in the frontend. */
/* File: frontend/app/sign-up/page.jsx */


import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#f7f7f8' }}>
      <SignUp routing="hash" />
    </div>
  );
}