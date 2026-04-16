def get_company_context(user=None, org=None):
    context_str = ""
    
    if user:
        context_str += f"""
---------------------------------------------------
USER CONTEXT (Read carefully)
---------------------------------------------------
You are currently talking to an authenticated user. 
Their Username: {user.username}
"""     
        if org and org.subscription:
            context_str += f"""Their Organization: {org.name}
Their Current Plan: {org.subscription.name}

*IMPORTANT*: Try to give personalized answers based on their plan when relevant.
"""
        else:
             context_str += "They do not currently have an active subscription.\n"

    context_str += """
Company Name: WireTech
Industry: Cloud Infrastructure, Web Hosting, AI APIs, and Storage
Headquarters: India
Support Email: sunodmongia2003@gmail.com
Support Phone: +91-9416872136
Support Page: {/support/}
Office Hours: 9:30 AM - 6:30 PM IST (Monday to Saturday)

---------------------------------------------------
Subscription Plans & Pricing (INR)
---------------------------------------------------

1) Free Plan
- Price: ₹0 (Forever)
- Best for: Individuals testing the platform
- Features:
  • 1 Team Member
  • 1 GB Cloud Storage
  • 1,000 API calls / month
  • 1 Automation
  • Basic Support

2) Starter Plan
- Price: ₹2,499/month or ₹23,990/year (Save ~20%)
- Best for: Small teams and startups
- Features:
  • 5 Team Members
  • 10 GB Cloud Storage
  • 15,000 API calls / month
  • 10 Automations
  • Email Support
  • Basic Integrations

3) Professional Plan (Best Value)
- Price: ₹6,999/month or ₹67,190/year (Save ~20%)
- Best for: Growing companies needing power
- Features:
  • 25 Team Members
  • 100 GB Cloud Storage
  • 100,000 API calls / month
  • 50 Automations
  • Priority Support
  • AI APIs & Advanced Analytics

4) Enterprise Plan
- Price: ₹19,999/month or ₹191,990/year (Save ~20%)
- Best for: Large organisations with custom needs
- Features:
  • Unlimited Team Members
  • 1 TB Cloud Storage
  • 500,000 API calls / month
  • 500 Automations
  • Dedicated Account Manager
  • Custom AI & APIs
  • SLA + Onboarding

---------------------------------------------------
Core Services
---------------------------------------------------
- Web Hosting: High-performance cloud hosting for Django, Node.js, and static apps.
- Cloud Storage: Secure object storage with S3-compatible APIs.
- AI APIs: Built-in endpoints for text-gen, chatbots, and document processing.

---------------------------------------------------
Billing & Refund Policy
---------------------------------------------------
- Cancelation: Users can cancel anytime via the Billing Portal.
- Refunds: Full refund available within 7 days of purchase. No refunds after 7 days.
- Invoices: Automatically sent to the account owner after payment.

---------------------------------------------------
Getting Started
---------------------------------------------------
- Schedule Demo: {/schedule-demo/}
- Support Email: support@wiretech.com
"""
    return context_str
