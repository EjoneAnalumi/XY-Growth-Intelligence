-- Synthetic Week 1 seed data. 30 Companies and 50 Contacts.
-- Generated to satisfy Week 1 Day 2 constraints.

INSERT INTO public.companies (
    id, name, domain, website, industry, company_size, employee_range, employee_count,
    annual_revenue_usd, headquarters_city, headquarters_country, cloud_usage, regulatory_context,
    lead_source, tags, status, lifecycle_stage, fit_score, last_activity_at, next_action, next_action_due_at
) VALUES
    ('10000000-0000-4000-8000-000000000001', 'Northstar Robotics Labs', 'northstar-robotics.example', 'https://northstar-robotics.example', 'Manufacturing Technology', 'mid-market', '201-500', 420, 48000000.00, 'Austin', 'United States', ARRAY['AWS', 'Azure'], ARRAY['SOC 2'], 'conference', ARRAY['robotics', 'cloud'], 'qualified', 'qualified', 84, NOW() - INTERVAL '3 days', 'Book discovery workshop', NOW() + INTERVAL '4 days'),
    ('10000000-0000-4000-8000-000000000002', 'Blue Harbor Finance', 'blueharbor-finance.example', 'https://blueharbor-finance.example', 'Financial Services', 'mid-market', '201-500', 260, 73000000.00, 'Boston', 'United States', ARRAY['Azure'], ARRAY['PCI DSS', 'SOX'], 'partner referral', ARRAY['finance', 'regulated'], 'prospect', 'prospect', 78, NOW() - INTERVAL '8 days', 'Send assessment overview', NOW() + INTERVAL '2 days'),
    ('10000000-0000-4000-8000-000000000003', 'Greenfield Health Systems', 'greenfield-health.example', 'https://greenfield-health.example', 'Healthcare', 'enterprise', '501-1000', 850, 126000000.00, 'Denver', 'United States', ARRAY['AWS', 'Google Cloud'], ARRAY['HIPAA'], 'web inquiry', ARRAY['healthcare', 'compliance'], 'qualified', 'qualified', 91, NOW() - INTERVAL '1 day', 'Confirm pilot sponsor', NOW() + INTERVAL '1 day'),
    ('10000000-0000-4000-8000-000000000004', 'Atlas Grid Utilities', 'atlas-grid.example', 'https://atlas-grid.example', 'Energy', 'enterprise', '501-1000', 620, 98000000.00, 'Phoenix', 'United States', ARRAY['Azure', 'Private Cloud'], ARRAY['NERC CIP'], 'industry event', ARRAY['energy', 'critical-infrastructure'], 'prospect', 'prospect', 73, NOW() - INTERVAL '15 days', 'Identify security owner', NOW() + INTERVAL '7 days'),
    ('10000000-0000-4000-8000-000000000005', 'Silverline Retail Group', 'silverline-retail.example', 'https://silverline-retail.example', 'Retail', 'mid-market', '201-500', 310, 54000000.00, 'Chicago', 'United States', ARRAY['AWS'], ARRAY['PCI DSS'], 'outbound research', ARRAY['retail', 'payments'], 'prospect', 'prospect', 69, NOW() - INTERVAL '5 days', 'Follow up on cloud security need', NOW() + INTERVAL '3 days'),
    ('10000000-0000-4000-8000-000000000006', 'Cobalt Cloud Services', 'cobalt-cloud.example', 'https://cobalt-cloud.example', 'Cloud Services', 'growth', '101-200', 145, 29000000.00, 'Seattle', 'United States', ARRAY['AWS', 'Kubernetes'], ARRAY['SOC 2', 'ISO 27001'], 'technical webinar', ARRAY['saas', 'cloud'], 'qualified', 'qualified', 88, NOW() - INTERVAL '2 days', 'Scope external exposure review', NOW() + INTERVAL '5 days'),
    ('10000000-0000-4000-8000-000000000007', 'Pioneer Logistics Network', 'pioneer-logistics.example', 'https://pioneer-logistics.example', 'Logistics', 'enterprise', '501-1000', 530, 67000000.00, 'Atlanta', 'United States', ARRAY['Azure'], ARRAY['SOC 2'], 'partner referral', ARRAY['logistics', 'supply-chain'], 'prospect', 'prospect', 76, NOW() - INTERVAL '11 days', 'Schedule stakeholder intro', NOW() + INTERVAL '6 days'),
    ('10000000-0000-4000-8000-000000000008', 'Summit Legal Partners', 'summit-legal.example', 'https://summit-legal.example', 'Legal Services', 'small-business', '51-100', 95, 18000000.00, 'New York', 'United States', ARRAY['Microsoft 365'], ARRAY['Client confidentiality'], 'conference', ARRAY['legal', 'privacy'], 'prospect', 'prospect', 63, NOW() - INTERVAL '20 days', 'Confirm decision process', NOW() + INTERVAL '9 days'),
    ('10000000-0000-4000-8000-000000000009', 'Meridian BioMaterials', 'meridian-biomaterials.example', 'https://meridian-biomaterials.example', 'Biotechnology', 'mid-market', '201-500', 210, 41000000.00, 'San Diego', 'United States', ARRAY['Google Cloud', 'AWS'], ARRAY['FDA validation', 'ISO 27001'], 'web inquiry', ARRAY['biotech', 'research'], 'qualified', 'qualified', 86, NOW() - INTERVAL '4 days', 'Send pilot assumptions', NOW() + INTERVAL '2 days'),
    ('10000000-0000-4000-8000-000000000010', 'Vector Learning Platforms', 'vector-learning.example', 'https://vector-learning.example', 'Education Technology', 'growth', '101-200', 180, 22000000.00, 'Raleigh', 'United States', ARRAY['AWS'], ARRAY['FERPA'], 'outbound research', ARRAY['edtech', 'saas'], 'prospect', 'prospect', 71, NOW() - INTERVAL '6 days', 'Share snapshot sample', NOW() + INTERVAL '8 days'),
    ('10000000-0000-4000-8000-000000000011', 'Apex Cyberspace', 'apex-cyber.example', 'https://apex-cyber.example', 'Cloud Services', 'growth', '101-200', 120, 15000000.00, 'Miami', 'United States', ARRAY['AWS'], ARRAY['SOC 2'], 'outbound research', ARRAY['cyber'], 'prospect', 'prospect', 70, NOW(), 'Intro call', NOW() + INTERVAL '1 day'),
    ('10000000-0000-4000-8000-000000000012', 'Beacon Media', 'beacon-media.example', 'https://beacon-media.example', 'Retail', 'small-business', '51-100', 60, 8000000.00, 'Orlando', 'United States', ARRAY['GCP'], ARRAY['GDPR'], 'web inquiry', ARRAY['media'], 'prospect', 'prospect', 65, NOW(), 'Follow up email', NOW() + INTERVAL '2 days'),
    ('10000000-0000-4000-8000-000000000013', 'Citadel Defense', 'citadel.example', 'https://citadel.example', 'Energy', 'enterprise', '501-1000', 700, 110000000.00, 'Washington', 'United States', ARRAY['Azure'], ARRAY['ITAR'], 'partner referral', ARRAY['defense'], 'qualified', 'qualified', 95, NOW(), 'Demo presentation', NOW() + INTERVAL '3 days'),
    ('10000000-0000-4000-8000-000000000014', 'Delta Quantum tech', 'delta-q.example', 'https://delta-q.example', 'Manufacturing Technology', 'growth', '101-200', 130, 24000000.00, 'San Jose', 'United States', ARRAY['AWS'], ARRAY['ISO 27001'], 'conference', ARRAY['quantum'], 'prospect', 'prospect', 80, NOW(), 'Send technical brief', NOW() + INTERVAL '4 days'),
    ('10000000-0000-4000-8000-000000000015', 'Echo Health', 'echo-health.example', 'https://echo-health.example', 'Healthcare', 'mid-market', '201-500', 340, 45000000.00, 'Dallas', 'United States', ARRAY['AWS'], ARRAY['HIPAA'], 'web inquiry', ARRAY['health'], 'qualified', 'qualified', 87, NOW(), 'Review compliance sheet', NOW() + INTERVAL '5 days'),
    ('10000000-0000-4000-8000-000000000016', 'Fox Fintech', 'fox-fin.example', 'https://fox-fin.example', 'Financial Services', 'growth', '101-200', 190, 35000000.00, 'Charlotte', 'United States', ARRAY['Azure'], ARRAY['PCI DSS'], 'partner referral', ARRAY['fintech'], 'prospect', 'prospect', 75, NOW(), 'Call executive sponsor', NOW() + INTERVAL '1 day'),
    ('10000000-0000-4000-8000-000000000017', 'Genesis Genomics', 'genesis-g.example', 'https://genesis-g.example', 'Biotechnology', 'mid-market', '201-500', 400, 60000000.00, 'San Francisco', 'United States', ARRAY['GCP'], ARRAY['FDA validation'], 'outbound research', ARRAY['genetics'], 'qualified', 'qualified', 89, NOW(), 'Scope pilot scope', NOW() + INTERVAL '3 days'),
    ('10000000-0000-4000-8000-000000000018', 'Horizon Logistics', 'horizon-log.example', 'https://horizon-log.example', 'Logistics', 'enterprise', '501-1000', 900, 130000000.00, 'Houston', 'United States', ARRAY['AWS'], ARRAY['SOC 2'], 'conference', ARRAY['shipping'], 'prospect', 'prospect', 72, NOW(), 'Introductory sync', NOW() + INTERVAL '6 days'),
    ('10000000-0000-4000-8000-000000000019', 'Ironclad Legal', 'ironclad-law.example', 'https://ironclad-law.example', 'Legal Services', 'small-business', '51-100', 80, 14000000.00, 'Philadelphia', 'United States', ARRAY['Microsoft 365'], ARRAY['Client confidentiality'], 'web inquiry', ARRAY['corporate-law'], 'prospect', 'prospect', 60, NOW(), 'Send contract proposal', NOW() + INTERVAL '2 days'),
    ('10000000-0000-4000-8000-000000000020', 'Jupiter EdTech', 'jupiter-ed.example', 'https://jupiter-ed.example', 'Education Technology', 'growth', '101-200', 160, 19000000.00, 'Nashville', 'United States', ARRAY['AWS'], ARRAY['FERPA'], 'outbound research', ARRAY['lms'], 'prospect', 'prospect', 68, NOW(), 'Setup demo environment', NOW() + INTERVAL '5 days'),
    ('10000000-0000-4000-8000-000000000021', 'Krypton Labs', 'krypton.example', 'https://krypton.example', 'Manufacturing Technology', 'small-business', '11-50', 45, 6000000.00, 'Detroit', 'United States', ARRAY['AWS'], ARRAY['ISO 27001'], 'conference', ARRAY['hardware'], 'prospect', 'prospect', 66, NOW(), 'Discovery call', NOW() + INTERVAL '4 days'),
    ('10000000-0000-4000-8000-000000000022', 'Lexington Wealth', 'lex-wealth.example', 'https://lex-wealth.example', 'Financial Services', 'mid-market', '201-500', 220, 50000000.00, 'Richmond', 'United States', ARRAY['Azure'], ARRAY['SOX'], 'partner referral', ARRAY['wealth-mgmt'], 'qualified', 'qualified', 82, NOW(), 'Align project timeline', NOW() + INTERVAL '2 days'),
    ('10000000-0000-4000-8000-000000000023', 'Matrix BioTech', 'matrix-bio.example', 'https://matrix-bio.example', 'Biotechnology', 'growth', '101-200', 110, 21000000.00, 'Seattle', 'United States', ARRAY['GCP'], ARRAY['FDA validation'], 'web inquiry', ARRAY['pharma'], 'prospect', 'prospect', 79, NOW(), 'Email product deck', NOW() + INTERVAL '1 day'),
    ('10000000-0000-4000-8000-000000000024', 'Nova Energy', 'nova-energy.example', 'https://nova-energy.example', 'Energy', 'enterprise', '501-1000', 550, 85000000.00, 'Denver', 'United States', ARRAY['Azure'], ARRAY['NERC CIP'], 'industry event', ARRAY['solar'], 'prospect', 'prospect', 74, NOW(), 'Find technical contact', NOW() + INTERVAL '7 days'),
    ('10000000-0000-4000-8000-000000000025', 'Omni Retail', 'omni-retail.example', 'https://omni-retail.example', 'Retail', 'enterprise', '501-1000', 980, 140000000.00, 'Minneapolis', 'United States', ARRAY['AWS'], ARRAY['PCI DSS'], 'outbound research', ARRAY['e-commerce'], 'qualified', 'qualified', 88, NOW(), 'Finalize architecture review', NOW() + INTERVAL '3 days'),
    ('10000000-0000-4000-8000-000000000026', 'Pulse Cloud Solutions', 'pulse-cloud.example', 'https://pulse-cloud.example', 'Cloud Services', 'small-business', '51-100', 85, 12000000.00, 'Salt Lake City', 'United States', ARRAY['AWS', 'Kubernetes'], ARRAY['SOC 2'], 'technical webinar', ARRAY['devops'], 'prospect', 'prospect', 77, NOW(), 'Schedule intro call', NOW() + INTERVAL '2 days'),
    ('10000000-0000-4000-8000-000000000027', 'Quantum Freight', 'quantum-freight.example', 'https://quantum-freight.example', 'Logistics', 'mid-market', '201-500', 410, 52000000.00, 'Memphis', 'United States', ARRAY['Azure'], ARRAY['SOC 2'], 'partner referral', ARRAY['freight'], 'prospect', 'prospect', 71, NOW(), 'Send case study', NOW() + INTERVAL '4 days'),
    ('10000000-0000-4000-8000-000000000028', 'Redwood Legal Group', 'redwood-legal.example', 'https://redwood-legal.example', 'Legal Services', 'mid-market', '201-500', 300, 38000000.00, 'San Francisco', 'United States', ARRAY['Microsoft 365'], ARRAY['Client confidentiality'], 'conference', ARRAY['compliance-law'], 'qualified', 'qualified', 83, NOW(), 'Review MSA changes', NOW() + INTERVAL '3 days'),
    ('10000000-0000-4000-8000-000000000029', 'Stellar Health Tech', 'stellar-health.example', 'https://stellar-health.example', 'Healthcare', 'growth', '101-200', 170, 26000000.00, 'Pittsburgh', 'United States', ARRAY['AWS', 'GCP'], ARRAY['HIPAA'], 'web inquiry', ARRAY['telehealth'], 'prospect', 'prospect', 76, NOW(), 'Qualify budget', NOW() + INTERVAL '5 days'),
    ('10000000-0000-4000-8000-000000000030', 'Titanium Systems', 'titanium-sys.example', 'https://titanium-sys.example', 'Manufacturing Technology', 'enterprise', '501-1000', 750, 105000000.00, 'Cleveland', 'United States', ARRAY['Azure'], ARRAY['ISO 27001'], 'outbound research', ARRAY['automation'], 'qualified', 'qualified', 90, NOW(), 'Schedule pilot kickoff', NOW() + INTERVAL '1 day')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, updated_at = NOW();

INSERT INTO public.contacts (
    id, company_id, first_name, last_name, email, phone, title, department, role, influence, decision_category, channels, last_contact_at, next_follow_up_at, is_primary
) VALUES
    ('20000000-0000-4000-8000-000000000001', '10000000-0000-4000-8000-000000000001', 'Mira', 'Vale', 'mira.vale@northstar-robotics.example', '+1-555-0101', 'VP Operations', 'Operations', 'Operational sponsor', 'high', 'champion', ARRAY['email', 'meeting'], NOW() - INTERVAL '3 days', NOW() + INTERVAL '4 days', true),
    ('20000000-0000-4000-8000-000000000002', '10000000-0000-4000-8000-000000000001', 'Jon', 'Keller', 'jon.keller@northstar-robotics.example', '+1-555-0102', 'Security Manager', 'Security', 'Technical evaluator', 'medium', 'influencer', ARRAY['email'], NOW() - INTERVAL '9 days', NOW() + INTERVAL '10 days', false),
    ('20000000-0000-4000-8000-000000000003', '10000000-0000-4000-8000-000000000002', 'Elena', 'Rossi', 'elena.rossi@blueharbor-finance.example', '+1-555-0103', 'CISO', 'Security', 'Security buyer', 'high', 'buyer', ARRAY['email', 'call'], NOW() - INTERVAL '8 days', NOW() + INTERVAL '2 days', true),
    ('20000000-0000-4000-8000-000000000004', '10000000-0000-4000-8000-000000000003', 'Samir', 'Patel', 'samir.patel@greenfield-health.example', '+1-555-0104', 'Director of Compliance', 'Compliance', 'Compliance sponsor', 'high', 'champion', ARRAY['email', 'workshop'], NOW() - INTERVAL '1 day', NOW() + INTERVAL '1 day', true),
    ('20000000-0000-4000-8000-000000000005', '10000000-0000-4000-8000-000000000004', 'Nadia', 'Brooks', 'nadia.brooks@atlas-grid.example', '+1-555-0105', 'Infrastructure Lead', 'IT', 'Technical stakeholder', 'medium', 'influencer', ARRAY['email'], NOW() - INTERVAL '15 days', NOW() + INTERVAL '7 days', true),
    ('20000000-0000-4000-8000-000000000006', '10000000-0000-4000-8000-000000000005', 'Carla', 'Nguyen', 'carla.nguyen@silverline-retail.example', '+1-555-0106', 'Payments Program Manager', 'Payments', 'Program owner', 'medium', 'champion', ARRAY['email', 'call'], NOW() - INTERVAL '5 days', NOW() + INTERVAL '3 days', true),
    ('20000000-0000-4000-8000-000000000007', '10000000-0000-4000-8000-000000000006', 'Theo', 'Martin', 'theo.martin@cobalt-cloud.example', '+1-555-0107', 'Head of Platform Security', 'Engineering', 'Technical buyer', 'high', 'buyer', ARRAY['email', 'demo'], NOW() - INTERVAL '2 days', NOW() + INTERVAL '5 days', true),
    ('20000000-0000-4000-8000-000000000008', '10000000-0000-4000-8000-000000000007', 'Iris', 'Cole', 'iris.cole@pioneer-logistics.example', '+1-555-0108', 'Procurement Lead', 'Procurement', 'Commercial gatekeeper', 'medium', 'procurement', ARRAY['email'], NOW() - INTERVAL '11 days', NOW() + INTERVAL '6 days', true),
    ('20000000-0000-4000-8000-000000000009', '10000000-0000-4000-8000-000000000008', 'Owen', 'Larsen', 'owen.larsen@summit-legal.example', '+1-555-0109', 'Managing Partner', 'Leadership', 'Executive sponsor', 'high', 'buyer', ARRAY['email', 'meeting'], NOW() - INTERVAL '20 days', NOW() + INTERVAL '9 days', true),
    ('20000000-0000-4000-8000-000000000010', '10000000-0000-4000-8000-000000000009', 'Lina', 'Meyer', 'lina.meyer@meridian-biomaterials.example', '+1-555-0110', 'Research Systems Owner', 'Research', 'Application owner', 'medium', 'influencer', ARRAY['email', 'workshop'], NOW() - INTERVAL '4 days', NOW() + INTERVAL '2 days', true),
    ('20000000-0000-4000-8000-000000000011', '10000000-0000-4000-8000-000000000010', 'Amara', 'Stone', 'amara.stone@vector-learning.example', '+1-555-0111', 'VP Product', 'Product', 'Business sponsor', 'medium', 'champion', ARRAY['email', 'demo'], NOW() - INTERVAL '6 days', NOW() + INTERVAL '8 days', true),
    ('20000000-0000-4000-8000-000000000012', '10000000-0000-4000-8000-000000000010', 'Noah', 'Reed', 'noah.reed@vector-learning.example', '+1-555-0112', 'IT Manager', 'IT', 'Technical contact', 'low', 'unknown', ARRAY['email'], NULL, NULL, false),
    ('20000000-0000-4000-8000-000000000013', '10000000-0000-4000-8000-000000000011', 'Alice', 'Smith', 'alice@apex-cyber.example', '+1-555-0113', 'CISO', 'Security', 'Security buyer', 'high', 'buyer', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000014', '10000000-0000-4000-8000-000000000011', 'Bob', 'Jones', 'bob@apex-cyber.example', '+1-555-0114', 'Engineer', 'IT', 'Technical contact', 'low', 'unknown', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000015', '10000000-0000-4000-8000-000000000012', 'Charlie', 'Brown', 'charlie@beacon-media.example', '+1-555-0115', 'Manager', 'Retail', 'Program owner', 'medium', 'champion', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000016', '10000000-0000-4000-8000-000000000012', 'David', 'Miller', 'david@beacon-media.example', '+1-555-0116', 'VP', 'Executive', 'Executive sponsor', 'high', 'buyer', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000017', '10000000-0000-4000-8000-000000000013', 'Emma', 'Davis', 'emma@citadel.example', '+1-555-0117', 'Director', 'Energy', 'Compliance sponsor', 'high', 'champion', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000018', '10000000-0000-4000-8000-000000000013', 'Frank', 'Wilson', 'frank@citadel.example', '+1-555-0118', 'Analyst', 'IT', 'Technical contact', 'low', 'unknown', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000019', '10000000-0000-4000-8000-000000000014', 'Grace', 'Lee', 'grace@delta-q.example', '+1-555-0119', 'CTO', 'Engineering', 'Technical buyer', 'high', 'buyer', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000020', '10000000-0000-4000-8000-000000000014', 'Henry', 'Taylor', 'henry@delta-q.example', '+1-555-0120', 'Lead', 'Engineering', 'Technical stakeholder', 'medium', 'influencer', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000021', '10000000-0000-4000-8000-000000000015', 'Ivy', 'Clark', 'ivy@echo-health.example', '+1-555-0121', 'CISO', 'Security', 'Security buyer', 'high', 'buyer', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000022', '10000000-0000-4000-8000-000000000015', 'Jack', 'White', 'jack@echo-health.example', '+1-555-0122', 'Manager', 'Healthcare', 'Program owner', 'medium', 'champion', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000023', '10000000-0000-4000-8000-000000000016', 'Kate', 'Harris', 'kate@fox-fin.example', '+1-555-0123', 'VP Finance', 'Finance', 'Executive sponsor', 'high', 'buyer', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000024', '10000000-0000-4000-8000-000000000016', 'Leo', 'Martin', 'leo@fox-fin.example', '+1-555-0124', 'Analyst', 'Finance', 'Technical contact', 'low', 'unknown', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000025', '10000000-0000-4000-8000-000000000017', 'Mia', 'Lewis', 'mia@genesis-g.example', '+1-555-0125', 'Director', 'Biotech', 'Compliance sponsor', 'high', 'champion', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000026', '10000000-0000-4000-8000-000000000017', 'Nick', 'Allen', 'nick@genesis-g.example', '+1-555-0126', 'Researcher', 'Research', 'Technical stakeholder', 'medium', 'influencer', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000027', '10000000-0000-4000-8000-000000000018', 'Olivia', 'Young', 'olivia@horizon-log.example', '+1-555-0127', 'VP Supply Chain', 'Logistics', 'Operational sponsor', 'high', 'champion', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000028', '10000000-0000-4000-8000-000000000018', 'Paul', 'King', 'paul@horizon-log.example', '+1-555-0128', 'Manager', 'Logistics', 'Program owner', 'medium', 'influencer', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000029', '10000000-0000-4000-8000-000000000019', 'Quinn', 'Wright', 'quinn@ironclad-law.example', '+1-555-0129', 'Partner', 'Legal', 'Executive sponsor', 'high', 'buyer', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000030', '10000000-0000-4000-8000-000000000019', 'Ryan', 'Scott', 'ryan@ironclad-law.example', '+1-555-0130', 'Clerk', 'Legal', 'Technical contact', 'low', 'unknown', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000031', '10000000-0000-4000-8000-000000000020', 'Sara', 'Green', 'sara@jupiter-ed.example', '+1-555-0131', 'VP Product', 'Product', 'Business sponsor', 'medium', 'champion', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000032', '10000000-0000-4000-8000-000000000020', 'Tom', 'Baker', 'tom@jupiter-ed.example', '+1-555-0132', 'Admin', 'IT', 'Technical contact', 'low', 'unknown', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000033', '10000000-0000-4000-8000-000000000021', 'Uma', 'Adams', 'uma@krypton.example', '+1-555-0133', 'Founder', 'Executive', 'Executive sponsor', 'high', 'buyer', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000034', '10000000-0000-4000-8000-000000000022', 'Victor', 'Nelson', 'victor@lex-wealth.example', '+1-555-0134', 'CISO', 'Security', 'Security buyer', 'high', 'buyer', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000035', '10000000-0000-4000-8000-000000000023', 'Wendy', 'Hill', 'wendy@matrix-bio.example', '+1-555-0135', 'Director', 'Biotech', 'Compliance sponsor', 'high', 'champion', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000036', '10000000-0000-4000-8000-000000000024', 'Xavier', 'Lopez', 'xavier@nova-energy.example', '+1-555-0136', 'Lead Engineer', 'IT', 'Technical stakeholder', 'medium', 'influencer', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000037', '10000000-0000-4000-8000-000000000025', 'Yara', 'Gomez', 'yara@omni-retail.example', '+1-555-0137', 'VP E-commerce', 'Retail', 'Program owner', 'medium', 'champion', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000038', '10000000-0000-4000-8000-000000000026', 'Zack', 'Carter', 'zack@pulse-cloud.example', '+1-555-0138', 'Head of Security', 'Security', 'Technical buyer', 'high', 'buyer', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000039', '10000000-0000-4000-8000-000000000027', 'Anna', 'Roberts', 'anna@quantum-freight.example', '+1-555-0139', 'Manager', 'Logistics', 'Program owner', 'medium', 'influencer', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000040', '10000000-0000-4000-8000-000000000028', 'Ben', 'Turner', 'ben@redwood-legal.example', '+1-555-0140', 'Managing Partner', 'Legal', 'Executive sponsor', 'high', 'buyer', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000041', '10000000-0000-4000-8000-000000000029', 'Chloe', 'Phillips', 'chloe@stellar-health.example', '+1-555-0141', 'Director Tech', 'Healthcare', 'Compliance sponsor', 'high', 'champion', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000042', '10000000-0000-4000-8000-000000000030', 'Dan', 'Parker', 'dan@titanium-sys.example', '+1-555-0142', 'VP Automation', 'Engineering', 'Technical buyer', 'high', 'buyer', ARRAY['email'], NOW(), NOW(), true),
    ('20000000-0000-4000-8000-000000000043', '10000000-0000-4000-8000-000000000001', 'Eva', 'Green', 'eva@northstar-robotics.example', '+1-555-0143', 'Developer', 'Engineering', 'Technical contact', 'low', 'unknown', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000044', '10000000-0000-4000-8000-000000000002', 'Fred', 'Stewart', 'fred@blueharbor-finance.example', '+1-555-0144', 'Risk Manager', 'Compliance', 'Technical evaluator', 'medium', 'influencer', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000045', '10000000-0000-4000-8000-000000000003', 'Gina', 'Morris', 'gina@greenfield-health.example', '+1-555-0145', 'Admin', 'IT', 'Technical contact', 'low', 'unknown', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000046', '10000000-0000-4000-8000-000000000004', 'Harry', 'Rogers', 'harry@atlas-grid.example', '+1-555-0146', 'Security Rep', 'Security', 'Technical contact', 'low', 'unknown', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000047', '10000000-0000-4000-8000-000000000005', 'Ian', 'Cook', 'ian@silverline-retail.example', '+1-555-0147', 'Lead Dev', 'IT', 'Technical contact', 'low', 'unknown', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000048', '10000000-0000-4000-8000-000000000006', 'Julia', 'Bell', 'julia@cobalt-cloud.example', '+1-555-0148', 'DevOps Eng', 'Engineering', 'Technical contact', 'low', 'unknown', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000049', '10000000-0000-4000-8000-000000000007', 'Kevin', 'Murphy', 'kevin@pioneer-logistics.example', '+1-555-0149', 'Analyst', 'IT', 'Technical contact', 'low', 'unknown', ARRAY['email'], NOW(), NOW(), false),
    ('20000000-0000-4000-8000-000000000050', '10000000-0000-4000-8000-000000000008', 'Lucy', 'Bailey', 'lucy@summit-legal.example', '+1-555-0150', 'Legal Assistant', 'Legal', 'Technical contact', 'low', 'unknown', ARRAY['email'], NOW(), NOW(), false)
ON CONFLICT (id) DO UPDATE SET first_name = EXCLUDED.first_name, updated_at = NOW();

-- Synthetic Week 2 seed expansion (brief shared Week 2 counts).
-- Known active seed metrics:
-- opportunities: 20 total, 17 open, 2 won, 1 lost
-- activities: 40 total
-- tasks: 25 total, with predictable overdue and due-this-week rows

INSERT INTO public.pipeline_stages (
    id, name, sort_order, default_probability, is_won, is_lost
) VALUES
    ('30000000-0000-4000-8000-000000000001', 'Identified', 10, 5, false, false),
    ('30000000-0000-4000-8000-000000000002', 'Researching', 20, 10, false, false),
    ('30000000-0000-4000-8000-000000000003', 'Contacted', 30, 15, false, false),
    ('30000000-0000-4000-8000-000000000004', 'Meeting Scheduled', 40, 25, false, false),
    ('30000000-0000-4000-8000-000000000005', 'Discovery Completed', 50, 35, false, false),
    ('30000000-0000-4000-8000-000000000006', 'Qualified', 60, 45, false, false),
    ('30000000-0000-4000-8000-000000000007', 'Assessment Offered', 70, 50, false, false),
    ('30000000-0000-4000-8000-000000000008', 'Pilot Proposed', 80, 60, false, false),
    ('30000000-0000-4000-8000-000000000009', 'Pilot Active', 90, 70, false, false),
    ('30000000-0000-4000-8000-000000000010', 'Proposal Sent', 100, 75, false, false),
    ('30000000-0000-4000-8000-000000000011', 'Negotiation', 110, 85, false, false),
    ('30000000-0000-4000-8000-000000000012', 'Contract Review', 120, 90, false, false),
    ('30000000-0000-4000-8000-000000000013', 'Won', 130, 100, true, false),
    ('30000000-0000-4000-8000-000000000014', 'Lost', 140, 0, false, true),
    ('30000000-0000-4000-8000-000000000015', 'On Hold', 150, 0, false, false)
ON CONFLICT (name) DO UPDATE SET
    id = EXCLUDED.id,
    sort_order = EXCLUDED.sort_order,
    default_probability = EXCLUDED.default_probability,
    is_won = EXCLUDED.is_won,
    is_lost = EXCLUDED.is_lost,
    updated_at = NOW();

INSERT INTO public.opportunities (
    id, company_id, contact_id, stage_id, name, service, value_usd, probability,
    weighted_value_usd, expected_close_date, need, blockers, competitor, next_action,
    next_action_due_at, created_at, updated_at
)
SELECT
    seed.id,
    seed.company_id,
    seed.contact_id,
    seed.stage_id,
    seed.name,
    seed.service,
    seed.value_usd,
    seed.probability,
    ROUND(seed.value_usd * seed.probability / 100, 2),
    seed.expected_close_date,
    seed.need,
    seed.blockers,
    seed.competitor,
    seed.next_action,
    seed.next_action_due_at,
    seed.created_at,
    seed.created_at
FROM (
    VALUES
        ('60000000-0000-4000-8000-000000000001'::uuid, '10000000-0000-4000-8000-000000000001'::uuid, '20000000-0000-4000-8000-000000000001'::uuid, '30000000-0000-4000-8000-000000000001'::uuid, 'Northstar SOC readiness sprint', 'Security Assessment', 20000.00, 5, CURRENT_DATE + 20, 'Validate current cloud controls', null, null, 'Confirm scope call', NOW() + INTERVAL '1 day', NOW() - INTERVAL '2 days'),
        ('60000000-0000-4000-8000-000000000002'::uuid, '10000000-0000-4000-8000-000000000002'::uuid, '20000000-0000-4000-8000-000000000003'::uuid, '30000000-0000-4000-8000-000000000002'::uuid, 'Blue Harbor incident readiness', 'Incident Response Retainer', 40000.00, 10, CURRENT_DATE + 28, 'Board requires response coverage', 'Budget owner not confirmed', null, 'Send retainer options', NOW() + INTERVAL '2 days', NOW() - INTERVAL '3 days'),
        ('60000000-0000-4000-8000-000000000003'::uuid, '10000000-0000-4000-8000-000000000003'::uuid, '20000000-0000-4000-8000-000000000004'::uuid, '30000000-0000-4000-8000-000000000003'::uuid, 'Greenfield HIPAA monitoring', 'Managed SOC', 60000.00, 15, CURRENT_DATE + 35, 'HIPAA audit remediation', null, 'Regional MSP', 'Book technical discovery', NOW() + INTERVAL '3 days', NOW() - INTERVAL '4 days'),
        ('60000000-0000-4000-8000-000000000004'::uuid, '10000000-0000-4000-8000-000000000004'::uuid, '20000000-0000-4000-8000-000000000005'::uuid, '30000000-0000-4000-8000-000000000004'::uuid, 'Atlas Grid exposure review', 'Attack Surface Management', 80000.00, 25, CURRENT_DATE + 42, 'Critical infrastructure exposure review', 'Procurement path unclear', null, 'Run stakeholder meeting', NOW() + INTERVAL '4 days', NOW() - INTERVAL '5 days'),
        ('60000000-0000-4000-8000-000000000005'::uuid, '10000000-0000-4000-8000-000000000005'::uuid, '20000000-0000-4000-8000-000000000006'::uuid, '30000000-0000-4000-8000-000000000005'::uuid, 'Silverline payment security plan', 'Cloud Security Review', 100000.00, 35, CURRENT_DATE + 49, 'PCI DSS cloud evidence gaps', null, 'Boutique assessor', 'Share findings summary', NOW() + INTERVAL '5 days', NOW() - INTERVAL '6 days'),
        ('60000000-0000-4000-8000-000000000006'::uuid, '10000000-0000-4000-8000-000000000006'::uuid, '20000000-0000-4000-8000-000000000007'::uuid, '30000000-0000-4000-8000-000000000006'::uuid, 'Cobalt managed detection pilot', 'Managed SOC', 120000.00, 45, CURRENT_DATE + 56, 'Need continuous Kubernetes monitoring', null, null, 'Draft pilot success criteria', NOW() + INTERVAL '6 days', NOW() - INTERVAL '7 days'),
        ('60000000-0000-4000-8000-000000000007'::uuid, '10000000-0000-4000-8000-000000000007'::uuid, '20000000-0000-4000-8000-000000000008'::uuid, '30000000-0000-4000-8000-000000000007'::uuid, 'Pioneer logistics assessment', 'Security Assessment', 140000.00, 50, CURRENT_DATE + 63, 'Supply-chain risk review', null, null, 'Send assessment proposal', NOW() + INTERVAL '7 days', NOW() - INTERVAL '8 days'),
        ('60000000-0000-4000-8000-000000000008'::uuid, '10000000-0000-4000-8000-000000000008'::uuid, '20000000-0000-4000-8000-000000000009'::uuid, '30000000-0000-4000-8000-000000000008'::uuid, 'Summit legal privacy monitoring', 'Managed SOC', 160000.00, 60, CURRENT_DATE + 70, 'Client confidentiality controls', 'Partner approval needed', null, 'Review pilot terms', NOW() + INTERVAL '8 days', NOW() - INTERVAL '9 days'),
        ('60000000-0000-4000-8000-000000000009'::uuid, '10000000-0000-4000-8000-000000000009'::uuid, '20000000-0000-4000-8000-000000000010'::uuid, '30000000-0000-4000-8000-000000000009'::uuid, 'Meridian bio research pilot', 'Cloud Security Review', 180000.00, 70, CURRENT_DATE + 77, 'Research environment monitoring', null, 'Lab IT provider', 'Confirm pilot timeline', NOW() + INTERVAL '9 days', NOW() - INTERVAL '10 days'),
        ('60000000-0000-4000-8000-000000000010'::uuid, '10000000-0000-4000-8000-000000000010'::uuid, '20000000-0000-4000-8000-000000000011'::uuid, '30000000-0000-4000-8000-000000000010'::uuid, 'Vector learning proposal', 'Security Assessment', 200000.00, 75, CURRENT_DATE + 84, 'FERPA roadmap needed', null, null, 'Send final proposal', NOW() + INTERVAL '10 days', NOW() - INTERVAL '11 days'),
        ('60000000-0000-4000-8000-000000000011'::uuid, '10000000-0000-4000-8000-000000000011'::uuid, '20000000-0000-4000-8000-000000000013'::uuid, '30000000-0000-4000-8000-000000000011'::uuid, 'Apex security negotiation', 'Managed SOC', 220000.00, 85, CURRENT_DATE + 91, 'SOC 2 readiness gap', 'Legal redlines pending', null, 'Resolve terms', NOW() + INTERVAL '11 days', NOW() - INTERVAL '12 days'),
        ('60000000-0000-4000-8000-000000000012'::uuid, '10000000-0000-4000-8000-000000000012'::uuid, '20000000-0000-4000-8000-000000000015'::uuid, '30000000-0000-4000-8000-000000000012'::uuid, 'Beacon retail contract review', 'Incident Response Retainer', 240000.00, 90, CURRENT_DATE + 98, 'Retail incident response coverage', null, null, 'Review contract edits', NOW() + INTERVAL '12 days', NOW() - INTERVAL '13 days'),
        ('60000000-0000-4000-8000-000000000013'::uuid, '10000000-0000-4000-8000-000000000013'::uuid, '20000000-0000-4000-8000-000000000017'::uuid, '30000000-0000-4000-8000-000000000013'::uuid, 'Citadel defense closed win', 'Managed SOC', 260000.00, 100, CURRENT_DATE - 5, 'Defense monitoring requirement', null, null, 'Schedule kickoff', NOW() + INTERVAL '13 days', NOW() - INTERVAL '14 days'),
        ('60000000-0000-4000-8000-000000000014'::uuid, '10000000-0000-4000-8000-000000000014'::uuid, '20000000-0000-4000-8000-000000000019'::uuid, '30000000-0000-4000-8000-000000000014'::uuid, 'Delta quantum lost pilot', 'Cloud Security Review', 280000.00, 20, CURRENT_DATE - 3, 'Manufacturing roadmap review', 'Selected incumbent provider', 'Incumbent provider', 'Capture lost reason', NOW() + INTERVAL '14 days', NOW() - INTERVAL '15 days'),
        ('60000000-0000-4000-8000-000000000015'::uuid, '10000000-0000-4000-8000-000000000015'::uuid, '20000000-0000-4000-8000-000000000021'::uuid, '30000000-0000-4000-8000-000000000015'::uuid, 'Echo health on hold', 'Security Assessment', 300000.00, 0, CURRENT_DATE + 110, 'HIPAA monitoring budget paused', 'Budget freeze', null, 'Revisit budget window', NOW() + INTERVAL '15 days', NOW() - INTERVAL '16 days'),
        ('60000000-0000-4000-8000-000000000016'::uuid, '10000000-0000-4000-8000-000000000016'::uuid, '20000000-0000-4000-8000-000000000023'::uuid, '30000000-0000-4000-8000-000000000001'::uuid, 'Fox fintech early deal', 'Incident Response Retainer', 50000.00, 5, CURRENT_DATE + 117, 'PCI response planning', null, null, 'Qualify sponsor', NOW() + INTERVAL '16 days', NOW() - INTERVAL '17 days'),
        ('60000000-0000-4000-8000-000000000017'::uuid, '10000000-0000-4000-8000-000000000017'::uuid, '20000000-0000-4000-8000-000000000025'::uuid, '30000000-0000-4000-8000-000000000006'::uuid, 'Genesis genomics qualified pilot', 'Managed SOC', 75000.00, 45, CURRENT_DATE + 124, 'Research security coverage', null, null, 'Align pilot owners', NOW() + INTERVAL '17 days', NOW() - INTERVAL '18 days'),
        ('60000000-0000-4000-8000-000000000018'::uuid, '10000000-0000-4000-8000-000000000018'::uuid, '20000000-0000-4000-8000-000000000027'::uuid, '30000000-0000-4000-8000-000000000010'::uuid, 'Horizon logistics proposal', 'Attack Surface Management', 125000.00, 75, CURRENT_DATE + 131, 'External footprint visibility', null, null, 'Send procurement pack', NOW() + INTERVAL '18 days', NOW() - INTERVAL '19 days'),
        ('60000000-0000-4000-8000-000000000019'::uuid, '10000000-0000-4000-8000-000000000019'::uuid, '20000000-0000-4000-8000-000000000029'::uuid, '30000000-0000-4000-8000-000000000011'::uuid, 'Ironclad legal negotiation', 'Security Assessment', 150000.00, 85, CURRENT_DATE + 138, 'Client data protection review', null, 'National consultancy', 'Confirm commercial approval', NOW() + INTERVAL '19 days', NOW() - INTERVAL '20 days'),
        ('60000000-0000-4000-8000-000000000020'::uuid, '10000000-0000-4000-8000-000000000020'::uuid, '20000000-0000-4000-8000-000000000031'::uuid, '30000000-0000-4000-8000-000000000013'::uuid, 'Jupiter edtech closed win', 'Cloud Security Review', 175000.00, 100, CURRENT_DATE - 1, 'FERPA review completed', null, null, 'Set renewal reminder', NOW() + INTERVAL '20 days', NOW() - INTERVAL '21 days')
) AS seed (
    id, company_id, contact_id, stage_id, name, service, value_usd, probability,
    expected_close_date, need, blockers, competitor, next_action, next_action_due_at,
    created_at
)
ON CONFLICT (id) DO UPDATE SET
    stage_id = EXCLUDED.stage_id,
    value_usd = EXCLUDED.value_usd,
    probability = EXCLUDED.probability,
    weighted_value_usd = EXCLUDED.weighted_value_usd,
    next_action = EXCLUDED.next_action,
    next_action_due_at = EXCLUDED.next_action_due_at,
    updated_at = NOW();

INSERT INTO public.activities (
    id, company_id, contact_id, opportunity_id, activity_type, subject, notes, occurred_at
)
SELECT
    ('40000000-0000-4000-8000-' || LPAD(series::text, 12, '0'))::uuid,
    ('10000000-0000-4000-8000-' || LPAD((((series - 1) % 30) + 1)::text, 12, '0'))::uuid,
    ('20000000-0000-4000-8000-' || LPAD((((series - 1) % 50) + 1)::text, 12, '0'))::uuid,
    ('60000000-0000-4000-8000-' || LPAD((((series - 1) % 20) + 1)::text, 12, '0'))::uuid,
    (ARRAY['call', 'email', 'meeting', 'demo', 'proposal', 'follow_up'])[((series - 1) % 6) + 1],
    'Seed activity ' || series,
    'Synthetic activity for dashboard metric verification.',
    NOW() - (series || ' days')::interval
FROM generate_series(1, 40) AS series
ON CONFLICT (id) DO UPDATE SET
    subject = EXCLUDED.subject,
    notes = EXCLUDED.notes,
    updated_at = NOW();

INSERT INTO public.tasks (
    id, company_id, opportunity_id, title, description, due_at, priority, status, completed_at
)
SELECT
    ('70000000-0000-4000-8000-' || LPAD(series::text, 12, '0'))::uuid,
    ('10000000-0000-4000-8000-' || LPAD((((series - 1) % 30) + 1)::text, 12, '0'))::uuid,
    ('60000000-0000-4000-8000-' || LPAD((((series - 1) % 20) + 1)::text, 12, '0'))::uuid,
    'Seed task ' || series,
    'Synthetic task for pipeline follow-up tracking.',
    CASE
        WHEN series <= 5 THEN NOW() - (series || ' days')::interval
        WHEN series <= 10 THEN NOW() + ((series - 5) || ' days')::interval
        ELSE NOW() + ((series + 7) || ' days')::interval
    END,
    (ARRAY['low', 'medium', 'high', 'urgent'])[((series - 1) % 4) + 1],
    CASE
        WHEN series IN (4, 9, 14) THEN 'completed'
        WHEN series IN (5, 10, 15) THEN 'in_progress'
        ELSE 'open'
    END,
    CASE
        WHEN series IN (4, 9, 14) THEN NOW() - INTERVAL '1 day'
        ELSE NULL
    END
FROM generate_series(1, 25) AS series
ON CONFLICT (id) DO UPDATE SET
    title = EXCLUDED.title,
    due_at = EXCLUDED.due_at,
    priority = EXCLUDED.priority,
    status = EXCLUDED.status,
    completed_at = EXCLUDED.completed_at,
    updated_at = NOW();

-- Synthetic Week 4 report-demo coverage required by the internship brief.
-- All targets are reserved example domains and all observations are deterministic.
INSERT INTO public.security_scans (
    id, company_id, initiated_by, domain, approval_note, approved, status,
    started_at, completed_at, duration_ms
) VALUES
    ('80000000-0000-4000-8000-000000000001', '10000000-0000-4000-8000-000000000001', '00000000-0000-4000-8000-000000000004', 'northstar-robotics.example', 'Approved synthetic demo target.', true, 'completed', NOW() - INTERVAL '12 days', NOW() - INTERVAL '12 days' + INTERVAL '2 seconds', 2000),
    ('80000000-0000-4000-8000-000000000002', '10000000-0000-4000-8000-000000000002', '00000000-0000-4000-8000-000000000004', 'blueharbor-finance.example', 'Approved synthetic demo target.', true, 'completed', NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days' + INTERVAL '3 seconds', 3000),
    ('80000000-0000-4000-8000-000000000003', '10000000-0000-4000-8000-000000000003', '00000000-0000-4000-8000-000000000004', 'greenfield-health.example', 'Approved synthetic demo target.', true, 'completed', NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days' + INTERVAL '1 second', 1000),
    ('80000000-0000-4000-8000-000000000004', '10000000-0000-4000-8000-000000000004', '00000000-0000-4000-8000-000000000004', 'atlas-grid.example', 'Approved synthetic demo target.', true, 'completed', NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days' + INTERVAL '4 seconds', 4000),
    ('80000000-0000-4000-8000-000000000005', '10000000-0000-4000-8000-000000000005', '00000000-0000-4000-8000-000000000004', 'silverline-retail.example', 'Approved synthetic demo target.', true, 'completed', NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days' + INTERVAL '2 seconds', 2000)
ON CONFLICT (id) DO UPDATE SET
    company_id = EXCLUDED.company_id,
    domain = EXCLUDED.domain,
    approval_note = EXCLUDED.approval_note,
    started_at = EXCLUDED.started_at,
    completed_at = EXCLUDED.completed_at,
    duration_ms = EXCLUDED.duration_ms;

INSERT INTO public.security_findings (
    security_scan_id, check_name, status, summary, finding, severity, method, evidence,
    error_classification, details
) VALUES
    ('80000000-0000-4000-8000-000000000001', 'dns', 'pass', 'Public DNS resolution completed.', false, 'info', 'deterministic mock', '["203.0.113.10"]', NULL, '{}'),
    ('80000000-0000-4000-8000-000000000001', 'tls', 'observation', 'TLS certificate expires within 30 days.', true, 'medium', 'deterministic mock', '["expires in 21 days"]', NULL, '{}'),
    ('80000000-0000-4000-8000-000000000002', 'http_headers', 'observation', 'Content-Security-Policy header was not observed.', true, 'low', 'deterministic mock', '["content-security-policy missing"]', NULL, '{}'),
    ('80000000-0000-4000-8000-000000000002', 'spf', 'pass', 'A single SPF record was observed.', false, 'info', 'deterministic mock', '["v=spf1 include:_spf.example -all"]', NULL, '{}'),
    ('80000000-0000-4000-8000-000000000003', 'dmarc', 'observation', 'DMARC monitoring policy was observed.', true, 'low', 'deterministic mock', '["v=DMARC1; p=none"]', NULL, '{}'),
    ('80000000-0000-4000-8000-000000000003', 'https', 'pass', 'HTTPS endpoint responded successfully.', false, 'info', 'deterministic mock', '["HTTP 200"]', NULL, '{}'),
    ('80000000-0000-4000-8000-000000000004', 'dns', 'timeout', 'DNS query timed out without a finding.', false, 'info', 'deterministic mock', '[]', 'timeout', '{}'),
    ('80000000-0000-4000-8000-000000000004', 'tls', 'error', 'TLS probe returned a classified connection error.', false, 'info', 'deterministic mock', '[]', 'connection_error', '{}'),
    ('80000000-0000-4000-8000-000000000005', 'spf', 'fail', 'No SPF record was observed.', true, 'medium', 'deterministic mock', '[]', NULL, '{}'),
    ('80000000-0000-4000-8000-000000000005', 'dmarc', 'pass', 'Enforcing DMARC policy was observed.', false, 'info', 'deterministic mock', '["v=DMARC1; p=reject"]', NULL, '{}')
ON CONFLICT (security_scan_id, check_name) DO UPDATE SET
    status = EXCLUDED.status,
    summary = EXCLUDED.summary,
    finding = EXCLUDED.finding,
    severity = EXCLUDED.severity,
    evidence = EXCLUDED.evidence,
    error_classification = EXCLUDED.error_classification;

-- Reports require real private Storage objects, which SQL alone cannot upload.
-- After this SQL seed, run from backend/: python -m app.seed_reports
-- That local-only command creates five real PDFs through the report workflow,
-- and is safe to repeat without rewinding existing report states.
