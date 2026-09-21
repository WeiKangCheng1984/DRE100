#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export the curated 280-point CA DRE cram sheet for the website."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_cram_items.json"
OUTPUT = ROOT / "data" / "cram280.json"

SECTION_TITLES = {
    "01": "Bundle of Rights, Land Traits & Value (DUST)",
    "02": "Real vs Personal Property, Fixtures & MARIA",
    "03": "Estates (Freehold / Leasehold)",
    "04": "Easements, Licenses & Liens",
    "05": "Agency & Listing Types",
    "06": "Contract Law Basics",
    "07": "Disclosures: TDS, NHD, Lead",
    "08": "Fair Housing & Ethics",
    "09": "Appraisal, CMA & Approaches",
    "10": "Income Approach & Investment (IRV)",
    "11": "Financing, Mortgages & Deeds of Trust",
    "12": "Deeds, Title & Notice",
    "13": "Land Description & Area",
    "14": "Leases, Landlord-Tenant & Property Mgmt",
    "15": "Environmental Hazards",
    "16": "Housing Types, Market & Profession",
    "17": "Escrow, Closing & High-Frequency Misc",
    "18": "-OR / -EE Pairings",
    "19": "Instant Exam Cues (See → Choose)",
}

# Each row is (exam-style English cue, correct association, trap/contrast).
# Grouping mirrors _cram_items.json so accidental reordering fails validation.
ENGLISH_BY_SECTION: dict[str, list[tuple[str, str, str]]] = {
    "01": [
        ("Bundle of rights", "Possession, use and enjoyment, exclusion, disposition, and control, subject to PETE", "Ownership is not immune from government police power."),
        ("PETE", "Police power, eminent domain, taxation, and escheat", "These are the four government powers over real property."),
        ("DUST elements of value", "Demand, utility, scarcity, and transferability", "Indestructibility is not an element of value."),
        ("Cloud on title", "Impaired transferability", "The missing element is not utility."),
        ("Immobility, indestructibility, and non-homogeneity", "The three physical characteristics of land", "Malleability is not a physical characteristic of land."),
        ("Situs", "Economic preference for location", "Do not confuse situs with illiquidity or inflation."),
        ("Assemblage", "The act or process of combining adjacent parcels", "Plottage is the resulting increase in value."),
        ("Plottage", "The added value created when combined parcels are worth more together", "The combining process itself is assemblage."),
        ("Accession", "Added property, natural or artificial, becomes part of the real property", "Accession includes processes such as accretion."),
        ("Accretion", "Gradual addition of land by deposited soil", "Reliction is land exposed by receding water."),
        ("Erosion vs. avulsion", "Erosion is gradual loss; avulsion is sudden removal by water", "Avulsion generally does not immediately change the boundary."),
        ("Principle of regression", "A higher-value property is pulled down by lower-value neighboring properties", "Progression is the opposite effect."),
        ("Principle of progression", "A lower-value property is enhanced by higher-value neighboring properties", "Regression is the opposite effect."),
        ("Market value", "The most probable price under typical market conditions", "Market price is the actual amount paid."),
        ("Assessed value", "Value set by the county assessor for property taxation", "California Proposition 13 limits increases in assessed value."),
        ("Stigmatized property", "Value impaired by psychological or social stigma rather than a physical defect", "A notorious event is not structural damage."),
    ],
    "02": [
        ("Real property", "Land, fixtures, and appurtenant rights", "Standing timber remains real property until severed."),
        ("Personal property / chattel", "Movable property and unattached materials", "Loose paving stones not installed are personal property."),
        ("Severance", "Changing real property into personal property by detaching it", "Cutting a tree is severance, not annexation."),
        ("Annexation", "Attaching personal property so it becomes a fixture", "Use the MARIA fixture test."),
        ("MARIA fixture test", "Method, adaptability, relationship, intention, and agreement", "When the agreement is silent, intention is often the key factor."),
        ("Trade fixture", "A business tenant's removable equipment, treated as personal property", "Remove it before the lease ends and repair any damage."),
        ("Appurtenance", "A right or improvement that runs with and transfers with the land", "It commonly transfers even if not separately stated in the deed."),
        ("Emblements / fructus industriales", "Annual crops produced by a tenant's labor", "Naturally growing plants are fructus naturales."),
        ("Encroachment", "A physical intrusion across a property line and continuing trespass", "An encroachment is not an easement."),
    ],
    "03": [
        ("Fee simple absolute", "The greatest ownership estate, inheritable and devisable by will", "A life estate ends at the measuring life and cannot be devised beyond it."),
        ("Fee simple determinable", "Title automatically reverts when the stated limitation is violated", "Look for durational words such as “so long as” or “until.”"),
        ("Fee simple subject to condition subsequent", "Grantor must exercise a right of re-entry to recover title after breach", "Title does not revert automatically."),
        ("Life estate", "An estate limited to the life of a named person", "It terminates at death and cannot be devised to children."),
        ("Pur autre vie", "A life estate measured by the life of another person", "The phrase means “for the life of another.”"),
        ("Estate for years", "A leasehold with definite beginning and ending dates", "It expires automatically without termination notice."),
        ("Periodic estate / estate from period to period", "A tenancy that renews automatically until proper notice is given", "Month-to-month is the common example."),
        ("Estate at will", "A tenancy that either party may terminate at will", "It has no fixed ending date."),
        ("Estate / tenancy at sufferance", "A holdover tenant remains after the lawful tenancy expires", "The landlord has not agreed to a new tenancy."),
        ("Four leasehold estates", "Estate for years, periodic estate, estate at will, and estate at sufferance", "A freehold estate is not a leasehold."),
    ],
    "04": [
        ("License", "A personal, usually revocable privilege to use another's land", "A license does not run with the land; oral parking permission is a common example."),
        ("Appurtenant easement", "An easement that runs with the land and benefits a dominant tenement", "It involves both a dominant and a servient tenement."),
        ("Easement in gross", "An easement benefiting a person or company rather than a dominant parcel", "Utility easements are common examples."),
        ("Easement by prescription", "An easement acquired through open, notorious, hostile, and continuous use for the statutory period", "It resembles adverse possession but creates use rights, not title."),
        ("Easement by necessity", "Access implied when a parcel would otherwise be landlocked", "It commonly arises when one parcel is divided."),
        ("Dominant and servient tenements", "The dominant tenement benefits; the servient tenement bears the easement", "The servient land carries the burden."),
        ("Mechanic's lien", "A lien securing payment for labor or materials improving real property", "It clouds title until paid or otherwise released."),
        ("Voluntary encumbrance", "An owner-created burden such as a deed of trust or mortgage", "It reduces unencumbered equity."),
        ("Deed restriction / CC&Rs", "A private restriction on how land may be used", "It is imposed privately, often by a developer."),
        ("Conflict between zoning and a deed restriction", "Comply with the more restrictive requirement", "Do not automatically choose public law or the least restrictive rule."),
        ("Racial or religious restrictive covenant", "Illegal, void, and unenforceable under fair housing law", "The invalid restriction generally does not invalidate the deed."),
        ("Illegal deed restriction", "The restriction is void, but title and the deed remain valid", "The property does not automatically revert."),
    ],
    "05": [
        ("Listing agreement", "Creates an agency relationship between the seller-client and listing broker", "A written agreement is the best practice."),
        ("Exclusive right-to-sell listing", "Full commission regardless of who sells, including an owner-sale", "This listing gives the broker the greatest protection."),
        ("Exclusive agency listing", "One broker is appointed, but the owner may sell without owing a commission", "Do not confuse it with exclusive right-to-sell."),
        ("Open listing", "Multiple brokers may compete; only the procuring cause earns the commission", "An owner-sale usually produces no commission."),
        ("Net listing", "Seller states a required net amount; broker may keep the excess as compensation", "Legal in California but risky and requiring full disclosure."),
        ("Procuring cause", "The uninterrupted chain of events that produces a ready, willing, and able buyer", "It is especially important in an open listing."),
        ("Protection / safety period", "Commission protection for a later sale to a prospect introduced during the listing", "It prevents avoiding commission by waiting for expiration."),
        ("Extinction of the subject matter", "Destruction of the property terminates the listing", "Fire or similar destruction is the usual fact pattern."),
        ("Performance as termination of agency", "Completion of the transaction and the agency purpose", "Performance is preferable to revocation or expiration."),
        ("Dual agency", "One broker represents both buyer and seller in the same transaction", "Requires disclosure and informed consent."),
        ("Fiduciary duties", "Loyalty, lawful obedience, reasonable care, accounting, and disclosure", "An agent must not obey an illegal instruction."),
        ("Ostensible agency / agency by estoppel", "A principal's conduct causes a third party reasonably to believe an agency exists", "The principal may be estopped from later denying the agency."),
        ("Buyer Representation and Broker Compensation Agreement (BRBC)", "The C.A.R. form is nonexclusive by default", "It does not become nonexclusive only when a special box is checked."),
        ("NAR member commission dispute", "Arbitration is generally required when one party properly requests it", "Waiver generally requires written agreement of all parties."),
        ("Law governing an agency relationship", "Agency law and contract law", "Agency principles generally control an agency-specific conflict."),
    ],
    "06": [
        ("Bilateral contract", "A promise exchanged for another promise", "A purchase agreement is the standard example."),
        ("Unilateral contract", "A promise exchanged for performance", "A reward is paid only when the requested act is completed."),
        ("Implied contract", "A contract inferred from conduct", "It is not an express written or oral agreement."),
        ("Express contract", "An agreement stated in words, either orally or in writing", ""),
        ("Executory contract", "A signed contract with obligations still unperformed", "Executed means all obligations have been completed."),
        ("Executed contract", "A contract in which both parties have fully performed", "A closed transaction is the usual example."),
        ("Void contract", "No legal effect from its inception", "Voidable means a protected party may elect to rescind."),
        ("When an offer becomes a binding contract", "The offeree accepts and communicates acceptance to the offeror", "Signing without communicating acceptance is insufficient."),
        ("Revocation of an offer", "The offeror may revoke before acceptance is communicated", "After effective acceptance, it is no longer merely an offer to revoke."),
        ("Counteroffer", "Rejection of the original offer and creation of a new offer", "The original offer is terminated."),
        ("Outstanding counteroffer and a new offer", "Withdraw the prior counteroffer before accepting the new offer", "This avoids obligations to two buyers."),
        ("Earnest money deposit", "A good-faith deposit showing serious intent", "It is not required consideration for contract formation."),
        ("Valuable consideration", "Legally sufficient consideration exchanged for a promise", "An empty or illusory promise may be insufficient."),
        ("Specific performance", "Court order requiring transfer of the particular real property", "Real property is considered unique."),
        ("Liquidated damages", "An agreed amount the seller may retain after a buyer's unjustified breach", "Often tied to the earnest money deposit."),
        ("Rescission", "Cancellation restoring the parties to their precontract positions", "It is not an order compelling closing."),
        ("Death of a contracting party", "Contract duties generally pass to the estate unless personal services are involved", "A listing is commonly treated as a personal-services agreement."),
        ("Statute of Frauds", "Most contracts involving real property must be in writing", "A lease for one year or less may be enforceable orally."),
        ("Nine-month lease", "May be enforceable without a writing", "An eighteen-month lease must be in writing."),
        ("Electronic signature", "Valid for real estate contracts when the parties consent", "E-SIGN and UETA support electronic transactions."),
        ("Doctrine of laches", "Unreasonable prejudicial delay can bar equitable relief", "Relief may be denied even before the statute of limitations expires."),
        ("Parol evidence rule", "Generally bars prior or contemporaneous oral terms that contradict an integrated writing", ""),
        ("Inspection contingency", "Allows cancellation or renegotiation based on unsatisfactory inspections", "A leaking roof is a typical fact pattern."),
        ("Appraisal contingency", "Protects the buyer if the property appraises below the contract price", "It may weaken an offer in a strong seller's market."),
        ("Financing contingency", "Allows the buyer to cancel if specified financing cannot be obtained", ""),
        ("Nature of a contingency", "A condition protecting a party's right to withdraw before satisfaction or removal", "An addendum is not itself a cancellation right."),
    ],
    "07": [
        ("Material fact", "A fact that could affect a buyer's decision or price and therefore must be disclosed", "An “as-is” clause does not excuse disclosure."),
        ("California “as-is” sale", "Seller declines repairs but must still disclose known material defects and complete required disclosures", "As-is does not mean no disclosure."),
        ("Transfer Disclosure Statement (TDS)", "Seller disclosure of known condition for one-to-four residential units", "School-district information is not part of the TDS."),
        ("Late personal delivery of the TDS", "Buyer generally has three days after personal delivery to cancel", "Delivery by mail or electronic transmission generally allows five days."),
        ("Foreclosure / REO sale", "Commonly exempt from the seller's TDS requirement", "A lender-owner often lacks personal knowledge of condition."),
        ("Natural Hazard Disclosure (NHD)", "Discloses mapped flood, fire, earthquake, and other natural hazard zones", "It is not the form specifically for asbestos or lead."),
        ("Lead-based paint disclosure", "Federal disclosure applies to most pre-1978 residential property", "A home built in 1964 is within the rule."),
        ("Latent defect", "A hidden defect not discoverable by ordinary inspection", "Asbestos behind drywall is a typical example."),
        ("Patent defect", "A defect that is open and readily observable", ""),
        ("Prior occupant with HIV/AIDS", "Do not disclose protected medical-status information", "Nondisclosure here complies with privacy and fair housing rules."),
        ("California death disclosure", "A death within the prior three years may require disclosure; an older natural death generally does not", "Apply the California Civil Code rule and answer direct questions truthfully as required."),
        ("Megan's Law / registered sex offenders", "Provide the standard statutory notice; a broker generally need not investigate independently", "Do not treat it exactly like a physical defect of the property."),
        ("Seller instructs agent to conceal a defect", "Refuse the illegal instruction, disclose as required, and consider terminating the agency", "Obedience does not extend to unlawful concealment."),
        ("Paint used to hide a foundation crack", "Disclose the concealed material defect or risk misrepresentation liability", "Do not advise the seller merely to improve the concealment."),
        ("C.A.R. Residential Purchase Agreement (RPA)", "A widely used industry form, not a single state-promulgated mandatory contract", "California does not prescribe it as the only statewide form."),
        ("Parties to a purchase agreement", "Buyer and seller", "The broker is ordinarily an agent, not a party to the sale contract."),
    ],
    "08": [
        ("Implicit bias", "Unconscious stereotypes that cause unequal service", "A person may sincerely claim fairness while acting on hidden assumptions."),
        ("Explicit bias", "Conscious, intentional discrimination", ""),
        ("Steering", "Directing people toward or away from neighborhoods based on a protected characteristic", "Steering violates fair housing law."),
        ("Blockbusting", "Inducing sales through fear that a protected group is entering the area", "Blockbusting is illegal."),
        ("Redlining", "Denying or restricting credit based on neighborhood or protected-group patterns", "Redlining is illegal."),
        ("Ethics vs. morals", "Ethics are external professional standards; morals are personal convictions", "The NAR Code of Ethics is an external standard."),
        ("Lack of competence in a specialized area", "Disclose the lack of expertise before providing the service", "NAR Article 11 addresses competence."),
        ("Commingling", "Mixing client trust funds with a broker's personal or business funds", "Conversion is actually taking or spending the client's money."),
        ("Appraisal fee based on appraised value", "Unethical and inconsistent with appraisal independence and USPAP", "Compensation cannot depend on reaching a particular value."),
        ("California Department of Real Estate (DRE)", "State agency that regulates real estate licenses", "C.A.R. and NAR are trade associations, not licensing enforcement agencies."),
        ("Real Estate Commissioner", "Head of the California Department of Real Estate", ""),
        ("Broker transaction-record retention", "Keep required transaction records for at least three years", "Count from closing or the relevant statutory event."),
    ],
    "09": [
        ("Appraisal", "A formal valuation performed by a properly licensed or certified appraiser", "The appraisal must comply with USPAP."),
        ("Comparative Market Analysis (CMA)", "A broker's informal pricing analysis; no appraiser license is required", "A CMA is not a formal appraisal."),
        ("Broker Price Opinion (BPO)", "A broker's opinion of property value or probable selling price", "It is less formal than an appraisal."),
        ("Sales comparison / market data approach", "Usually the best approach for existing owner-occupied homes", ""),
        ("Cost approach", "Best suited to new construction and special-purpose properties", "Land value plus replacement or reproduction cost minus depreciation."),
        ("Income approach", "Used for income-producing property", "Apply the IRV relationship."),
        ("Selecting CMA comparables", "Use nearby, similar sales, preferably from the last six to twelve months", "A comparable twenty-five miles away is usually too distant."),
        ("Direction of comparable adjustments", "Adjust the comparable, never the subject property", "If the comparable lacks a bathroom, add its value to the comparable's price."),
        ("Farm area / farming", "Building specialized market knowledge and prospects in a defined geographic area", "It does not mean agriculture or indiscriminate citywide marketing."),
        ("Listing price", "The seller's initial asking price", "It is not necessarily the final sale price."),
    ],
    "10": [
        ("Potential Gross Income (PGI)", "Income at 100% occupancy before vacancy or collection loss", "No vacancy allowance has yet been deducted."),
        ("Effective Gross Income (EGI)", "PGI minus vacancy and collection loss plus other income", "Operating expenses have not yet been deducted."),
        ("Net Operating Income (NOI)", "EGI minus operating expenses", "NOI normally excludes debt service and income taxes."),
        ("Capitalization rate", "NOI divided by value", "IRV states Income = Rate × Value."),
        ("Value by direct capitalization", "NOI divided by the capitalization rate", "Annualize monthly NOI before dividing."),
        ("Monthly NOI of $10,000 at a 6% cap rate", "Annual NOI is $120,000; value is $2,000,000", "Do not divide monthly NOI directly by the annual cap rate."),
        ("NOI of $25,000 and price of $500,000", "Capitalization rate is 5%", "Do not choose 10% or 20%."),
        ("Profit after routine operating expenses", "Use Net Operating Income (NOI)", "PGI and EGI are measured before operating expenses."),
        ("Income after vacancy but before operating expenses", "Use Effective Gross Income (EGI)", ""),
        ("High capitalization rate", "Generally indicates higher risk and a lower value relative to income", "A lower cap rate generally indicates the reverse."),
    ],
    "11": [
        ("Trustor", "Borrower who conveys bare legal title under a deed of trust", "The -or is the party giving or creating the interest."),
        ("Trustee under a deed of trust", "Neutral third party holding bare legal title for the security instrument", ""),
        ("Beneficiary under a deed of trust", "Lender whose loan is secured by the deed of trust", "The beneficiary receives the benefit of the security."),
        ("Mortgagor", "Borrower who gives the mortgage", "The mortgagee is the lender."),
        ("Optionor", "Party granting the option, usually the seller", "The optionee is the prospective buyer."),
        ("Grantor and grantee", "Grantor transfers title; grantee receives title", ""),
        ("Loan-to-value ratio (LTV)", "Loan amount divided by property value", "A high LTV conventional loan may require PMI."),
        ("Private mortgage insurance (PMI)", "Insurance protecting a conventional lender on a high-LTV loan", ""),
        ("Qualifying ratios", "Housing payment-to-income ratio and total debt-to-income ratio", "LTV is not a borrower qualifying ratio."),
        ("Interest-only monthly payment", "Principal multiplied by annual interest rate, divided by twelve", "$140,000 × 4.9% ÷ 12 = $571.67."),
        ("Monthly interest on an amortized loan", "Calculated on the remaining principal balance", "Early payments contain a larger interest portion."),
        ("Tight money market", "Interest rates, points, and loan costs tend to rise", "Credit does not become cheaper."),
        ("Increase in the supply of loan funds", "Interest rates tend to fall", ""),
        ("Sale-leaseback advantage", "The former owner may deduct rent as a business operating expense", ""),
        ("RESPA violation", "Paying or receiving a kickback for settlement-service referrals", "Example: a title company pays for referrals."),
        ("Truth in Lending Act (TILA)", "Requires disclosure of the true cost and terms of consumer credit", "TILA does not set market interest rates."),
    ],
    "12": [
        ("California grant deed", "Carries implied covenants that title was not previously conveyed and has no undisclosed grantor-created encumbrances", ""),
        ("Quitclaim deed", "Conveys whatever present interest the grantor may have, with no title warranties", "Often used to clear a cloud or release a possible claim."),
        ("Warranty deed", "Provides broad title warranties and covenants", "Its use and covenant details vary by state."),
        ("Bargain and sale deed", "Implies the grantor holds transferable title but provides few warranties", ""),
        ("Habendum clause", "The “to have and to hold” clause defining the estate granted", ""),
        ("Granting clause", "Operative words showing the grantor's intent to transfer title", ""),
        ("Delivery and acceptance of a deed", "Both are required for the deed to become effective", "The grantor's signature alone is insufficient."),
        ("Recording an instrument", "Gives constructive notice to the world", ""),
        ("Actual notice", "Direct, personal knowledge of a fact", ""),
        ("Constructive notice", "Knowledge imputed by law because the public record could be examined", ""),
        ("Abstract of title", "A summarized history of recorded instruments affecting title", "It is a report, not a title plant."),
        ("Title plant", "A title company's organized database of land and title records", ""),
        ("Marketable title", "Title reasonably free from significant defects and encumbrances", "It is title a prudent buyer can accept and later resell."),
        ("Chain of title", "The successive history of ownership transfers", ""),
        ("Legal description", "A description sufficient to identify one specific parcel", "A street address is not a legal description."),
        ("Reservation / exception in a deed", "Withholds a right or excludes an existing interest from the grant", ""),
        ("Probate", "Court-supervised administration of a decedent's estate", "Testate means with a will; intestate means without one."),
        ("Adverse possession", "Acquisition of title through open, notorious, hostile, continuous possession meeting statutory requirements", ""),
        ("Dedication / public grant", "Dedication transfers private land to public use; a public grant transfers public land to a private party", ""),
    ],
    "13": [
        ("Metes and bounds description", "Begins at a point of beginning and follows bearings and distances back to the POB", "Often references monuments or benchmarks and degrees, minutes, and seconds."),
        ("Government / rectangular survey", "Uses principal meridians, baselines, townships, ranges, and sections", "A notation such as T2S R2W identifies the grid location."),
        ("Lot and block / recorded plat", "Identifies a parcel by lot, block, and recorded subdivision map", ""),
        ("One acre", "43,560 square feet", "Two acres equal 87,120 square feet."),
        ("One section", "Usually 640 acres", "A standard section is one mile by one mile."),
    ],
    "14": [
        ("Assignment of a lease", "Assignee takes the tenant's entire remaining leasehold and commonly pays rent directly to the landlord", ""),
        ("Sublease / sublet", "Subtenant pays rent to the original tenant, who retains a reversionary interest", "Do not treat the subtenant as a direct replacement tenant under an assignment."),
        ("Gross lease", "Tenant pays fixed rent while the landlord pays most operating expenses", ""),
        ("Net lease", "Tenant pays rent plus specified taxes, insurance, maintenance, or other expenses", ""),
        ("Percentage lease", "Base rent plus a percentage of the tenant's gross sales", "Common in retail property."),
        ("Step-up / graduated lease", "Rent increases at stated intervals", ""),
        ("Unlawful detainer", "Court action used by a landlord to regain possession lawfully", "A landlord may not use self-help such as changing locks or shutting off utilities."),
        ("Constructive eviction", "Landlord's wrongful acts or omissions make the premises unusable and force the tenant to leave", "It is not a lawful eviction method."),
        ("California residential security-deposit limit", "Generally one month's rent under current law, subject to statutory exceptions", "Check the current Civil Code and any stated exception in the question."),
        ("Security-deposit accounting and return", "Generally provide the itemized statement and remaining deposit within 21 days after move-out", "Apply the current California Civil Code."),
        ("Regular pesticide use at rental property", "Landlord must give the tenant required notice", ""),
        ("Property management", "Managing rental property for another for compensation", ""),
        ("Terms not ordinarily included in a basic lease", "A future purchase option requires a separate lease-option provision", "Term, property description, and signatures are ordinary lease essentials."),
    ],
    "15": [
        ("Friable asbestos-containing material", "Can be crumbled by hand pressure, allowing fibers to become airborne", "Asbestosis is a disease, not a material condition."),
        ("Asbestos", "Naturally occurring mineral fibers formerly used for insulation; inhalation damages lungs", "Do not confuse it with radon, CFCs, or lead."),
        ("Radon", "Colorless, odorless radioactive gas that can enter through foundation cracks", "It results from uranium decay."),
        ("Lead hazard", "Commonly associated with older paint and plumbing; pre-1978 housing triggers federal disclosure", ""),
        ("UFFI", "Urea-formaldehyde foam insulation", ""),
        ("CFCs", "Chlorofluorocarbons formerly used in refrigerants and air-conditioning equipment", ""),
        ("HVAC", "Heating, ventilation, and air conditioning", "The H does not mean home."),
        ("Wastewater lines", "Pipes carrying wastewater away from a dwelling", "Municipal water lines bring potable water in."),
    ],
    "16": [
        ("Custom home", "Built for an identified buyer to that buyer's specifications", ""),
        ("Spec / speculative home", "Built without a specific buyer in anticipation of a later sale", ""),
        ("Tract home", "One of many standardized model homes in a planned development", ""),
        ("Warehouse classification", "Industrial real estate", "It is not agricultural property or ordinary retail space."),
        ("Industrial property", "Warehousing, manufacturing, and logistics uses", ""),
        ("Large employer enters a small town", "Population and housing demand rise; constrained supply tends to increase prices", ""),
        ("Increase in housing supply", "Prices tend to fall, all else equal", ""),
        ("Real estate specialization", "A licensee may specialize by property, client, service, or geographic market", "A different real estate license is not necessarily required."),
        ("REIT advantage", "Shares are relatively liquid and trade much like stocks", "Returns may differ from and sometimes trail direct property ownership."),
        ("Office building commanding the highest rent", "Usually a Class A building", ""),
        ("Most precise formal valuation product", "An appraisal", "It is more authoritative than a CMA or BPO."),
        ("NAR Code of Ethics", "Professional ethical guidance for REALTORS®", "NAR is not a government licensing enforcement agency."),
    ],
    "17": [
        ("California escrow holder", "A qualified person or entity may handle escrow under a statutory licensing exemption", "Select the party that meets the exemption stated in the question."),
        ("Closing", "Completion of the transaction and title transfer", "Before closing, the purchase contract is generally executory."),
        ("Title insurance", "Protection against covered title defects and risks", ""),
        ("Dominant mineral estate", "Mineral owner may make reasonable use of the surface to extract minerals", "Surface ownership does not automatically defeat valid mineral rights."),
        ("Covenant of quiet enjoyment", "Protects lawful possession from interference by a landlord or superior title claimant", "It is not a promise of silence and does not erase valid mineral rights."),
        ("Holographic will", "A will whose material provisions are in the testator's handwriting", "Merely signing an X is insufficient; ink color is not the issue."),
        ("Multiple Listing Service (MLS)", "A cooperative listing database and marketing system", "MLS is not a legal listing-agreement type."),
        ("Ready, willing, and able buyer", "A buyer meeting the seller's terms, often supporting procuring cause and commission entitlement", ""),
        ("Unit-in-place, square-foot, and quantity-survey methods", "Cost-estimating methods used in the cost approach to appraisal", ""),
        ("Prorations", "Allocation of taxes, rents, and similar expenses or income as of closing", ""),
    ],
    "18": [
        ("Party name ending in -OR", "Usually the party who gives, grants, or originates the right", "Examples: grantor, optionor, mortgagor, trustor, lessor, and vendor."),
        ("Party name ending in -EE", "Usually the party who receives the right or interest", "Examples: grantee, optionee, mortgagee, lessee, and vendee; deed-of-trust roles depend on context."),
        ("Incorrect -OR / -EE pairing", "Optionor is the option grantor, usually the seller—not the buyer", "Watch for questions asking for the incorrect pairing."),
        ("Lessor and lessee", "Lessor is landlord; lessee is tenant", ""),
        ("Vendor and vendee", "Vendor is seller; vendee is buyer, especially under a land contract", ""),
    ],
    "19": [
        ("See: commission is owed regardless of who produces the buyer", "Exclusive right-to-sell listing", ""),
        ("See: one exclusive broker, but owner may sell without commission", "Exclusive agency listing", ""),
        ("See: multiple brokers; only the procuring broker earns commission", "Open listing", ""),
        ("See: broker keeps proceeds above the seller's required amount", "Net listing", ""),
        ("See: breach of condition requires court action or re-entry to recover title", "Fee simple subject to condition subsequent", ""),
        ("See: “so long as” and automatic reversion", "Fee simple determinable", ""),
        ("See: month-to-month tenancy requiring notice to terminate", "Periodic tenancy", ""),
        ("See: tenant holds over after expiration without landlord consent", "Tenancy at sufferance", ""),
        ("See: revocable oral permission to park without charge", "License", ""),
        ("See: comparable sale located 25 miles away", "Reject it as an excessively distant comparable", ""),
        ("See: appraisal of new construction", "Cost approach", ""),
        ("See: appraisal of an income-producing commercial building", "Income approach", ""),
        ("See: comparison with recent similar sales", "Sales comparison approach", ""),
        ("See: residential property built before 1978, such as 1964", "Federal lead-based paint disclosure", ""),
        ("See: radon entering through foundation cracks", "Foundation cracks are a common radon entry route", ""),
        ("See: asbestos material that can be crumbled by hand pressure", "Friable asbestos-containing material", "Do not choose asbestosis, which is a disease."),
        ("See: appraisal fee increases with the appraised value", "Unethical contingency compensation; appraisal fee may not depend on value", ""),
        ("See: an “as-is” sale supposedly eliminates disclosures", "False—required disclosures, including the TDS when applicable, still apply", ""),
        ("See: earnest money is supposedly required to form a contract", "False—earnest money shows good faith but is not required consideration", ""),
        ("See: buyer breaches and the question asks the common agreed remedy", "Seller may retain the earnest money as liquidated damages, subject to the agreement and law", ""),
        ("See: seller has a counteroffer outstanding but wants to accept another offer", "Withdraw the outstanding counteroffer before accepting the new offer", ""),
        ("See: who receives rent from a subtenant", "The original tenant / sublessor", ""),
        ("See: required broker transaction-record retention period", "At least three years", ""),
        ("See: lease term of one year or less", "An oral lease may be enforceable under the Statute of Frauds exception", ""),
        ("See: TDS in a foreclosure or REO sale", "The transfer is commonly exempt from the seller TDS requirement", ""),
        ("See: whether school-district information belongs in the TDS", "It is not included in the TDS", ""),
        ("See: whether a broker must investigate and report registered sex offenders", "No independent investigation is generally required; give the statutory Megan's Law notice", ""),
        ("See: best way to create or document an agency relationship", "Put the agency agreement in writing", ""),
        ("See: when an offer becomes binding", "When acceptance is communicated to the offeror", ""),
        ("See: legal effect of a counteroffer", "It rejects the original offer and creates a new offer", ""),
        ("See: act of combining adjacent parcels", "Assemblage", ""),
        ("See: added value resulting from combined parcels", "Plottage", ""),
        ("See: high-value home surrounded by lower-value homes", "Principle of regression", ""),
        ("See: title defect makes property difficult to sell", "Transferability is impaired", ""),
        ("See: value reduced by psychological stigma rather than physical damage", "Stigmatized property", ""),
        ("See: income at full occupancy before vacancy loss", "Potential Gross Income (PGI)", ""),
        ("See: income after vacancy loss but before operating expenses", "Effective Gross Income (EGI)", ""),
        ("See: income after operating expenses", "Net Operating Income (NOI)", ""),
        ("See: I / R / V", "Income = Rate × Value", ""),
        ("See: monthly NOI used to calculate value", "Multiply by 12, then divide annual NOI by the capitalization rate", ""),
        ("See: who may perform a formal appraisal", "A properly licensed or certified appraiser", ""),
        ("See: whether a CMA requires an appraiser license", "No—real estate licensees may prepare a CMA as a pricing opinion", ""),
        ("See: client instructs the agent to conceal a material defect", "Refuse the instruction and make the legally required disclosure", ""),
        ("See: unconscious stereotyped assumptions", "Implicit bias", ""),
        ("See: client trust money mixed with the broker's own funds", "Commingling", ""),
        ("See: broker spends or takes client trust funds", "Conversion", ""),
        ("See: REALTOR® lacks expertise in the requested service", "Disclose the lack of competence before providing the service", ""),
        ("See: ethics versus morals", "Ethics are external professional rules; morals are personal convictions", ""),
        ("See: head of the California DRE", "Real Estate Commissioner", ""),
        ("See: agency regulating California real estate licenses", "California Department of Real Estate (DRE), not C.A.R.", ""),
        ("See: POB, bearings, distances, degrees, minutes, and seconds", "Metes and bounds", ""),
        ("See: township, range, and section", "Government / rectangular survey system", ""),
        ("See: quitclaim deed", "Conveys any present interest without title warranties", ""),
        ("See: recording a deed", "Constructive notice", ""),
        ("See: summarized report of a title search", "Abstract of title", ""),
        ("See: “to have and to hold”", "Habendum clause", ""),
    ],
}

EXPECTED_COUNTS = {
    "01": 16, "02": 9, "03": 10, "04": 12, "05": 15, "06": 26,
    "07": 16, "08": 12, "09": 10, "10": 10, "11": 16, "12": 19,
    "13": 5, "14": 13, "15": 8, "16": 12, "17": 10, "18": 5, "19": 56,
}

QUICK_CARDS = [
    {
        "en": "Listing four: Right-to-sell (full commission) / Agency (owner-sale exception) / Open (procuring cause) / Net (excess).",
        "zh": "Listing 四兄弟：Right-to-sell（全佣）／Agency（自售免）／Open（促成）／Net（超額）",
    },
    {
        "en": "Four leaseholds: Estate for years / Periodic / At will / At sufferance.",
        "zh": "租賃四兄弟：Years／Periodic／Will／Sufferance",
    },
    {
        "en": "Income ladder: PGI → EGI → NOI; Value = NOI ÷ Cap rate. Annualize monthly NOI first.",
        "zh": "收益三階：PGI → EGI → NOI → ÷Cap＝Value（月 NOI 先×12）",
    },
    {
        "en": "Three approaches: Sales comparison (existing homes) / Cost (new construction) / Income (investment).",
        "zh": "估價三法：比較（中古）／成本（新屋）／收益（投資）",
    },
    {
        "en": "Three disclosures: TDS (condition) / NHD (hazard zones) / Lead (pre-1978).",
        "zh": "揭露三表：TDS（屋況）／NHD（災害區）／Lead（1978前）",
    },
    {
        "en": "As-is does not waive disclosure; generally do not volunteer AIDS/sex-offender information; refuse concealment.",
        "zh": "As-is ≠ 免揭露；AIDS／性罪犯通常不主動揭；客戶叫隱瞞＝拒絕",
    },
    {
        "en": "-OR gives; -EE receives. The optionor is normally the seller, not the buyer.",
        "zh": "-OR 給、-EE 收；Optionor 是賣方不是買方",
    },
    {
        "en": "When zoning and a deed restriction conflict, obey the stricter rule; racial/religious restrictions are void.",
        "zh": "Deed 衝突跟最嚴；種族宗教限制＝無效",
    },
    {
        "en": "Acceptance must be communicated; withdraw a counter before accepting another; specific performance means that unique property.",
        "zh": "接受要送達；Counter 先撤再收；Specific performance＝要那棟屋",
    },
    {
        "en": "Friable ≠ asbestosis; radon enters through foundation cracks; keep records 3 years; hand-delivered TDS gives 3 days.",
        "zh": "Friable≠Asbestosis；Radon＝地基縫；3年存檔；親送TDS＝3天",
    },
]


def split_section(raw_section: str) -> tuple[str, str]:
    section_id, section_zh = raw_section.split(" ", 1)
    if section_id not in SECTION_TITLES:
        raise ValueError(f"Unknown section ID: {section_id}")
    return section_id, section_zh


def build_payload() -> dict[str, object]:
    source_items = json.loads(SOURCE.read_text(encoding="utf-8"))
    if len(source_items) != 280:
        raise ValueError(f"Expected 280 source tuples, got {len(source_items)}")

    for section_id, expected in EXPECTED_COUNTS.items():
        actual = len(ENGLISH_BY_SECTION[section_id])
        if actual != expected:
            raise ValueError(
                f"Section {section_id}: expected {expected} English rows, got {actual}"
            )

    section_order: list[str] = []
    section_zh_by_id: dict[str, str] = {}
    offsets = {section_id: 0 for section_id in SECTION_TITLES}
    items: list[dict[str, object]] = []

    for item_id, raw in enumerate(source_items, start=1):
        if not isinstance(raw, list) or len(raw) != 4:
            raise ValueError(f"Source item {item_id} is not a four-element tuple")
        raw_section, cue_zh, answer_zh, trap_zh = raw
        section_id, section_zh = split_section(raw_section)
        if section_id not in section_order:
            section_order.append(section_id)
            section_zh_by_id[section_id] = section_zh

        row_index = offsets[section_id]
        try:
            cue_en, answer_en, trap_en = ENGLISH_BY_SECTION[section_id][row_index]
        except IndexError as exc:
            raise ValueError(
                f"Missing English row for source item {item_id} ({section_id})"
            ) from exc
        offsets[section_id] += 1

        if not cue_en.strip() or not answer_en.strip():
            raise ValueError(f"Empty English cue/answer at item {item_id}")
        items.append(
            {
                "id": item_id,
                "sectionId": section_id,
                "sectionZh": section_zh,
                "sectionEn": SECTION_TITLES[section_id],
                "cueEn": cue_en,
                "cueZh": cue_zh,
                "answerEn": answer_en,
                "answerZh": answer_zh,
                "trapEn": trap_en,
                "trapZh": trap_zh,
            }
        )

    unused = {
        section_id: len(ENGLISH_BY_SECTION[section_id]) - offsets[section_id]
        for section_id in SECTION_TITLES
        if len(ENGLISH_BY_SECTION[section_id]) != offsets[section_id]
    }
    if unused:
        raise ValueError(f"English/source row mismatch: {unused}")

    sections = [
        {
            "id": section_id,
            "zh": section_zh_by_id[section_id],
            "en": SECTION_TITLES[section_id],
        }
        for section_id in section_order
    ]
    return {
        "titleZh": "考前衝刺 280 關鍵知識點",
        "titleEn": "CA DRE Cram Sheet — 280 Key Associations",
        "subtitleZh": "看到英文題幹關鍵詞 → 立刻聯想正確答案",
        "subtitleEn": "See the keyword → pick the linked answer. Exam stems are in English.",
        "sections": sections,
        "items": items,
        "quickCards": QUICK_CARDS,
    }


def main() -> None:
    payload = build_payload()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(payload['items'])} items -> {OUTPUT}")


if __name__ == "__main__":
    main()
