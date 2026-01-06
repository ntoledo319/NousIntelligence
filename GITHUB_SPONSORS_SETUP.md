# GitHub Sponsors Setup Guide

This guide walks you through setting up GitHub Sponsors for NOUS Intelligence.

## Prerequisites

- GitHub account with verified email
- Stripe Connect account (GitHub will guide you through setup)
- Bank account for receiving payments

## Step-by-Step Setup

### 1. Enable GitHub Sponsors

1. Go to your GitHub profile
2. Click "Sponsor" → "Join the waitlist" (if not already enabled)
3. Wait for approval (usually 1-2 days)

### 2. Set Up Stripe Connect

1. Once approved, go to https://github.com/sponsors
2. Click "Set up GitHub Sponsors"
3. Connect your Stripe account
4. Verify your identity
5. Add bank account information

### 3. Configure Sponsorship Tiers

Use these recommended tiers (already configured in SPONSORS.md):

**Tier 1: Supporter ($1/month)**
- Description: "You believe in the mission of accessible mental health tools"
- Benefits:
  - Recognition in README
  - Sponsor badge

**Tier 2: Advocate ($5/month)**
- Description: "You want monthly updates on development"
- Benefits:
  - All Supporter benefits
  - Monthly development updates
  - Early access to new features

**Tier 3: Champion ($10/month)**
- Description: "You're invested in the project's success"
- Benefits:
  - All Advocate benefits
  - Priority issue response
  - Name in CONTRIBUTORS.md

**Tier 4: Founding Sponsor ($25/month)**
- Description: "You're making this project possible"
- Benefits:
  - All Champion benefits
  - Logo/link on website
  - Quarterly video calls
  - Strategic input

**Custom Tier ($50+/month)**
- Description: "For organizations needing custom support"
- Benefits: Contact for custom arrangements

### 4. Create Sponsor Profile

Write your sponsor profile:

```markdown
# Support Accessible Mental Health Technology

NOUS Intelligence is making evidence-based mental health tools (CBT, DBT, AA) 
free and accessible to everyone. Your sponsorship funds:

- 🔧 Feature development
- 🏗️ Infrastructure & hosting
- 📚 Documentation & tutorials
- 🌍 Scaling to serve more users

## Current Goals

- $50/month - Cover hosting costs when we scale
- $100/month - Part-time development (10 hrs/month)
- $300/month - Weekend development
- $1000/month - Full-time development

## Impact

For the cost of a coffee per month, you help provide free mental health 
support to thousands who can't afford $300/month therapy.

[View Roadmap](https://github.com/ntoledo319/NousIntelligence/blob/main/SPONSORSHIP_ROADMAP.md)
```

### 5. Add FUNDING.yml

The file `.github/FUNDING.yml` is already created. This makes the "Sponsor" 
button appear on your repository.

### 6. Link to Sponsor Documentation

Update these files to reference sponsorship:

- ✅ README.md - "Support This Project" section
- ✅ SPONSORS.md - Full sponsor documentation
- ✅ FUNDING.yml - GitHub configuration

### 7. Promote Your Sponsorship

**Announcement Checklist:**

- [ ] Tweet about launching GitHub Sponsors
- [ ] Post in relevant Reddit communities (r/opensource, r/mentalhealth)
- [ ] Share in developer Discord/Slack communities
- [ ] Email beta testers
- [ ] Post in GitHub Discussions
- [ ] Update LinkedIn

**Sample Announcement:**

```
🎉 We've launched GitHub Sponsors for NOUS Intelligence!

NOUS is an open-source mental health platform providing free CBT, DBT, 
and AA tools. We're making therapy techniques accessible to everyone.

For the cost of a coffee/month, you can support:
✅ Free mental health tools
✅ Open source innovation
✅ Accessible healthcare

Sponsor: https://github.com/sponsors/ntoledo319
Learn more: https://github.com/ntoledo319/NousIntelligence

#opensource #mentalhealth #github
```

### 8. Set Up Monthly Updates

**Template for Monthly Updates:**

```markdown
# NOUS Development Update - [Month Year]

Hey sponsors! 👋

## This Month's Progress

✅ Completed:
- [Feature 1]
- [Feature 2]
- [Bug fixes]

🚧 In Progress:
- [Feature 3]
- [Feature 4]

## Metrics

- Stars: [count]
- Forks: [count]
- Active users: [estimate]
- Test coverage: [%]

## Next Month

- [Priority 1]
- [Priority 2]
- [Priority 3]

## Thank You

Your support makes this possible. Questions? Reply to this update!

- [Your Name]
```

### 9. Manage Sponsors

**Track sponsor benefits:**

Create a simple spreadsheet:
| Sponsor | Tier | Start Date | Benefits Delivered |
|---------|------|------------|-------------------|
| ...     | ...  | ...        | README ✅, Updates ✅ |

**Deliver benefits:**
- Add supporters to README monthly
- Send monthly updates to Advocates+
- Respond to Champion issues within 24hrs
- Schedule quarterly calls with Founding Sponsors

### 10. Financial Management

**Best Practices:**

1. **Transparency:** Share how funds are used
2. **Updates:** Keep sponsors informed monthly
3. **Recognition:** Thank sponsors publicly
4. **Deliver:** Follow through on tier benefits
5. **Reinvest:** Use funds for project development

**Tax Considerations:**

- GitHub Sponsors payments are **income**
- Track as self-employment income
- Consult accountant for tax obligations
- Keep records of development expenses

## Troubleshooting

### "Sponsor button not showing"

- Check `.github/FUNDING.yml` is in main branch
- Verify GitHub Sponsors is enabled on your account
- Wait up to 24 hours for cache refresh

### "Can't set up Stripe"

- Ensure you're 18+
- Have valid ID for verification
- Bank account in supported country
- Contact GitHub Support if issues persist

### "No sponsors yet"

**Be patient and:**
- Share project widely
- Show value through documentation
- Engage community
- Deliver quality work
- Be transparent about needs

## Checklist

Before launching GitHub Sponsors:

- [ ] GitHub Sponsors approved for your account
- [ ] Stripe Connect configured
- [ ] Bank account verified
- [ ] Sponsorship tiers created
- [ ] Sponsor profile written
- [ ] FUNDING.yml added to repo
- [ ] Documentation updated (README, SPONSORS.md)
- [ ] Announcement drafted
- [ ] Social media accounts ready
- [ ] Monthly update template prepared

## Resources

- [GitHub Sponsors Documentation](https://docs.github.com/en/sponsors)
- [Stripe Connect](https://stripe.com/connect)
- [Open Source Sustainability](https://opensource.guide/getting-paid/)

## Questions?

Open an issue or discussion in the repository.

Good luck! 🚀
