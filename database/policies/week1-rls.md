# Week 1 RLS Notes

This document summarizes the first Row Level Security policy set for the Day 2 schema.

## Roles

The migration uses the project roles from the brief:

- `admin`
- `management`
- `business_development`
- `technical_analyst`
- `read_only`

## Profiles

- Authenticated users can read their own profile.
- `admin` users can read all profiles.
- New authenticated users can insert only their own profile and only with the default `read_only` role.
- Users can update their own profile fields, but a trigger blocks non-admin users from changing `role` or `active`.
- `admin` users can update profile records, including role and active status.

## Companies

- Any authenticated active profile can read non-archived companies.
- Only `admin`, `management`, and `business_development` can insert companies.
- Only `admin`, `management`, and `business_development` can update companies.
- Inserts must set `created_by = auth.uid()` and `updated_by = auth.uid()`.
- Updates must set `updated_by = auth.uid()`.
- No hard-delete policy is defined. Business records should be archived with `archived_at`.

## Contacts

- Any authenticated active profile can read non-archived contacts for non-archived companies.
- Only `admin`, `management`, and `business_development` can insert contacts.
- Only `admin`, `management`, and `business_development` can update contacts.
- Inserts must set `created_by = auth.uid()` and `updated_by = auth.uid()`.
- Updates must set `updated_by = auth.uid()`.
- No hard-delete policy is defined. Business records should be archived with `archived_at`.

## Explicit Deny Cases

- `read_only` cannot insert or update companies.
- `read_only` cannot insert or update contacts.
- `technical_analyst` cannot insert or update companies or contacts in Week 1 CRM scope.
- Anonymous users cannot read, insert, or update any Week 1 table.
- Non-admin users cannot make themselves `admin`, `management`, `business_development`, or `technical_analyst`.
- No `delete` policy or authenticated `delete` grant is defined; business records use `archived_at`.

## Grants

- `authenticated` receives `select`, `insert`, and `update` grants on `profiles`, `companies`, and `contacts`.
- RLS policies still decide which rows and roles can use those privileges.
- `delete` is explicitly revoked from `anon` and `authenticated`.

## Manual Test Checklist

- Sign in as `business_development`, insert a company with matching `created_by` and `updated_by`, and confirm it succeeds.
- Sign in as `read_only`, select companies and contacts, and confirm reads succeed.
- Sign in as `read_only`, attempt to insert or update a company, and confirm it is rejected by RLS.
- Sign in as `technical_analyst`, attempt to insert or update a contact, and confirm it is rejected by RLS.
- Sign in as a non-admin user, attempt to update their own profile `role`, and confirm the trigger rejects it.
