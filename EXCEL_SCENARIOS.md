# Excel Data Setup Scenarios

## Comprehensive Guide to Advanced Excel Scenarios

This guide explains how to structure Excel data for different relationship types and field scenarios.

---

## 1. Simple Lookup (Standard entityreference)

### Scenario
You have a Contact entity with a lookup to Account (many contacts belong to one account).

### Excel Setup

| contactid | firstname | lastname | accountid |
|-----------|-----------|----------|-----------|
| C001 | John | Doe | A123 |
| C002 | Jane | Smith | A456 |

### Schema XML
```xml
<entity name="contact" displayname="Contact" primaryidfield="contactid">
  <fields>
    <field name="contactid" type="string" displayname="Contact ID"/>
    <field name="firstname" type="string" displayname="First Name"/>
    <field name="lastname" type="string" displayname="Last Name"/>
    <field name="accountid" type="entityreference" displayname="Account" target="account"/>
  </fields>
</entity>
```

### Result XML
```xml
<record id="C001">
  <field name="firstname" value="John"/>
  <field name="lastname" value="Doe"/>
  <field name="accountid" value="A123" lookupentity="account" lookupentityname="default"/>
</record>
```

---

## 2. Polymorphic Lookup (Multiple possible entities)

### Scenario
A Task can reference different entity types:
- Account
- Contact  
- Opportunity

You need to indicate WHICH type each reference is pointing to.

### Excel Setup

**Create TWO columns:**

| taskid | subject | **regardingobjectid** | **regardingobjectid_entityreference** |
|--------|---------|---------------------|---------------------------------------|
| T001 | Call customer | ACC123 | account |
| T002 | Follow up | CON456 | contact |
| T003 | Review proposal | OPP789 | opportunity |

### Naming Convention
```
{fieldname}_entityreference
```

**Examples:**
- `parentcustomerid_entityreference`
- `regardingobjectid_entityreference`
- `referringobjectid_entityreference`

### Schema XML
```xml
<entity name="task" displayname="Task" primaryidfield="taskid">
  <fields>
    <field name="taskid" type="string" displayname="Task ID"/>
    <field name="subject" type="string" displayname="Subject"/>
    <field name="regardingobjectid" type="entityreference" displayname="Regarding" 
           target="account|contact|opportunity"/>  <!-- Multiple possible targets -->
  </fields>
</entity>
```

### Result XML
```xml
<record id="T001">
  <field name="subject" value="Call customer"/>
  <field name="regardingobjectid" value="ACC123" lookupentity="account" lookupentityname="default"/>
</record>
<record id="T002">
  <field name="subject" value="Follow up"/>
  <field name="regardingobjectid" value="CON456" lookupentity="contact" lookupentityname="default"/>
</record>
```

**Key Point:** The `_entityreference` column tells the converter which entity type to use in the XML lookup!

---

## 3. Many-to-Many (M2M) Relationships

### Scenario
Contacts have multiple categories (sports). Categories have multiple contacts.
This is a junction/bridge table scenario.

### Excel Setup

**Option A: Composite Table (Recommended)**

Create a table named: `{entity1}_{entity2}` or `Contact_SportsCategory`

| contactid | ntg_sportcategoryid |
|-----------|---------------------|
| C001 | CAT001 |
| C001 | CAT002 |
| C002 | CAT001 |
| C002 | CAT003 |

### Schema XML
```xml
<schema>
  <!-- Entity 1 -->
  <entity name="contact" displayname="Contact" primaryidfield="contactid">
    <fields>
      <field name="contactid" type="string" displayname="Contact ID"/>
      <field name="firstname" type="string" displayname="First Name"/>
    </fields>
  </entity>

  <!-- Entity 2 -->
  <entity name="ntg_sportcategory" displayname="Sport Category" primaryidfield="ntg_sportcategoryid">
    <fields>
      <field name="ntg_sportcategoryid" type="string" displayname="ID"/>
      <field name="ntg_name" type="string" displayname="Name"/>
    </fields>
  </entity>

  <!-- Relationship Definition -->
  <relationships>
    <m2m name="contact_ntg_sportcategory" entity1="contact" entity1pk="contactid" 
         entity2="ntg_sportcategory" entity2pk="ntg_sportcategoryid"/>
  </relationships>
</schema>
```

### Result XML
```xml
<m2mrelationships>
  <m2mrelationship name="contact_ntg_sportcategory">
    <records>
      <record id1="C001" id2="CAT001"/>
      <record id1="C001" id2="CAT002"/>
      <record id1="C002" id2="CAT001"/>
      <record id1="C002" id2="CAT003"/>
    </records>
  </m2mrelationship>
</m2mrelationships>
```

**Key Points:**
- M2M table name must match schema m2m relationship name
- Only needs two columns: the primary IDs of both entities
- Don't include other data in M2M table
- No duplicate pairs allowed

---

## 4. Partylist (Complex Nested Relationships)

### Scenario
An Appointment has multiple required attendees (Contacts).
Each attendee has metadata like participation status, role, etc.
This creates nested XML structures.

### Excel Setup

**Main Table: Appointment**

| appointmentid | subject | scheduledstart | scheduledend |
|-------|---------|-----------------|----------------|
| APT001 | Team Meeting | 15.03.2024 10:00:00 | 15.03.2024 11:00:00 |
| APT002 | Client Call | 16.03.2024 14:00:00 | 16.03.2024 14:30:00 |

**Partylist Table: `partylist_requiredattendees`**

| appointmentid | contactid | role | participationstatus |
|-------|-----------|------|----------------------|
| APT001 | C001 | 1 | 3 |
| APT001 | C002 | 1 | 3 |
| APT002 | C001 | 3 | 5 |

### Naming Convention
```
partylist_{fieldname}
```

**The plural/field name after `partylist_` must match:**
- The field name in schema for the partylist field
- Exactly as defined in schema (case-sensitive)

**Examples:**
- `partylist_requiredattendees`
- `partylist_organizer`
- `partylist_participants`

### Schema XML
```xml
<entity name="appointment" displayname="Appointment" primaryidfield="appointmentid">
  <fields>
    <field name="appointmentid" type="string" displayname="ID"/>
    <field name="subject" type="string" displayname="Subject"/>
    <field name="scheduledstart" type="datetime" displayname="Start"/>
    <field name="scheduledend" type="datetime" displayname="End"/>
    <!-- Partylist field definition -->
    <field name="requiredattendees" type="partylist" displayname="Required Attendees"/>
  </fields>
</entity>
```

### Result XML
```xml
<record id="APT001">
  <field name="subject" value="Team Meeting"/>
  <field name="scheduledstart" value="2024-03-15T10:00:00Z"/>
  <field name="scheduledend" value="2024-03-15T11:00:00Z"/>
  <field name="requiredattendees">
    <partylistmember>
      <field name="partyid" value="C001"/>
      <field name="partytypecode" value="contact"/>
      <field name="role" value="1"/>
      <field name="participationstatus" value="3"/>
    </partylistmember>
    <partylistmember>
      <field name="partyid" value="C002"/>
      <field name="partytypecode" value="contact"/>
      <field name="role" value="1"/>
      <field name="participationstatus" value="3"/>
    </partylistmember>
  </field>
</record>
```

**Key Points:**
- First column MUST be the parent entity's primary key
- Second column MUST be named exactly as in schema partylist field name
- Third column onwards are metadata fields
- Contact ID is automatically extracted and wrapped

---

## 5. Owner Field (Special entityreference)

### Scenario
A Contact has an Owner (user/system user).

### Excel Setup

| contactid | firstname | lastname | ownerid |
|-----------|-----------|----------|---------|
| C001 | John | Doe | USR123 |

### Schema XML
```xml
<field name="ownerid" type="owner" displayname="Owner"/>
```

### Result XML
```xml
<field name="ownerid" value="USR123" lookupentity="systemuser" lookupentityname="default"/>
```

**Key Points:**
- `owner` type is a special entityreference to systemuser
- Setup same as entityreference column
- Automatically resolves to systemuser entity

---

## 6. Complete Real-World Example

### Excel Structure

**File: `CRM_Data.xlsx`**

#### Sheet/Table: `contact`
| contactid | firstname | lastname | accountid | ownerid | parentcustomerid | parentcustomerid_entityreference |
|-----------|-----------|----------|-----------|---------|------------------|----------------------------------|
| C001 | John | Doe | ACC123 | USR001 | P001 | account |
| C002 | Jane | Smith | ACC456 | USR002 | C001 | contact |

#### Sheet/Table: `appointment`
| appointmentid | subject | scheduledstart | scheduledend | regardingobjectid | regardingobjectid_entityreference |
|-------|---------|-----------------|----------------|-------------------|-------------------------------------|
| APT001 | Team Meeting | 15.03.2024 10:00:00 | 15.03.2024 11:00:00 | ACC123 | account |
| APT002 | Client Call | 16.03.2024 14:00:00 | 16.03.2024 14:30:00 | C001 | contact |

#### Sheet/Table: `partylist_requiredattendees`
| appointmentid | requiredattendees | role | participationstatus |
|-------|--------|------|----------------------|
| APT001 | C001 | 1 | 3 |
| APT001 | C002 | 1 | 3 |
| APT002 | C001 | 3 | 5 |

#### Sheet/Table: `ntg_sportcategory`
| ntg_sportcategoryid | ntg_name |
|-----|----------|
| CAT001 | Football |
| CAT002 | Basketball |
| CAT003 | Tennis |

#### Sheet/Table: `contact_ntg_sportcategory`
| contactid | ntg_sportcategoryid |
|-----------|---------------------|
| C001 | CAT001 |
| C001 | CAT002 |
| C002 | CAT001 |

### Schema XML
```xml
<?xml version="1.0" encoding="utf-8"?>
<schema>
  <entity name="contact" displayname="Contact" primaryidfield="contactid">
    <fields>
      <field name="contactid" type="string" displayname="Contact ID"/>
      <field name="firstname" type="string" displayname="First Name"/>
      <field name="lastname" type="string" displayname="Last Name"/>
      <field name="accountid" type="entityreference" displayname="Account" target="account"/>
      <field name="ownerid" type="owner" displayname="Owner"/>
      <field name="parentcustomerid" type="entityreference" displayname="Parent Customer" 
             target="account|contact"/>
    </fields>
  </entity>

  <entity name="appointment" displayname="Appointment" primaryidfield="appointmentid">
    <fields>
      <field name="appointmentid" type="string" displayname="ID"/>
      <field name="subject" type="string" displayname="Subject"/>
      <field name="scheduledstart" type="datetime" displayname="Start"/>
      <field name="scheduledend" type="datetime" displayname="End"/>
      <field name="regardingobjectid" type="entityreference" displayname="Regarding" 
             target="account|contact"/>
      <field name="requiredattendees" type="partylist" displayname="Required Attendees"/>
    </fields>
  </entity>

  <entity name="ntg_sportcategory" displayname="Sport Category" primaryidfield="ntg_sportcategoryid">
    <fields>
      <field name="ntg_sportcategoryid" type="string" displayname="ID"/>
      <field name="ntg_name" type="string" displayname="Name"/>
    </fields>
  </entity>

  <relationships>
    <m2m name="contact_ntg_sportcategory" entity1="contact" entity1pk="contactid" 
         entity2="ntg_sportcategory" entity2pk="ntg_sportcategoryid"/>
  </relationships>
</schema>
```

---

## Quick Reference Table

| Scenario | Excel Column(s) | Table Name | Schema Type | Notes |
|----------|-----------------|-----------|-------------|-------|
| Simple Lookup | `fieldname` | Entity table | `entityreference` | Direct ID reference |
| Polymorphic Lookup | `fieldname` + `fieldname_entityreference` | Entity table | `entityreference` with `\|` targets | Two columns needed |
| Owner | `ownerid` | Entity table | `owner` | Always references systemuser |
| M2M Relationship | `entity1id` + `entity2id` | `entity1_entity2` | m2m in schema | Junction table |
| Partylist | First col: Parent ID, Second: Field name | `partylist_{fieldname}` | `partylist` in schema | Nested relationship |

---

## Troubleshooting

### M2M Not Working
```
Issue: M2M records not appearing in output
Solution: 
- Check table name EXACTLY matches schema m2m name (case-sensitive)
- Ensure both entity IDs exist in their respective entities
- Verify schema has <m2m> relationship definition
```

### Polymorphic Lookup Missing Entity Type
```
Issue: lookupentity="null" in output XML
Solution:
- Add {fieldname}_entityreference column to Excel
- Fill with entity name (account, contact, etc.)
- Verify values match valid entity names in schema
```

### Partylist Records Not Appearing
```
Issue: No partylist members in output
Solution:
- Table MUST be named: partylist_{fieldname}
- First column MUST be parent entity's primary key
- Second column name must match the field name in schema
- Verify contact IDs exist in contact entity
```

### M2M Not Parsing
```
Issue: M2M relationship shows empty
Solution:
- Verify contact1_contact2 has exactly 2 columns
- Check IDs exist in both entity tables
- Ensure schema has relationship definition
```

---

## Tips

✅ **DO:**
- Use consistent naming (lowercase, underscores)
- Test with simple relationships first
- Verify schema defines the relationship correctly
- Check primary keys match between tables

❌ **DON'T:**
- Mix relationship types in one table
- Use spaces in table/column names
- Include extra columns in M2M tables
- Skip the `_entityreference` column for polymorphic lookups

---

## Excel vs Generated XML Reference

| Excel | XML Element | Purpose |
|-------|------------|---------|
| `accountid = "A123"` | `<field name="accountid" value="A123" lookupentity="account"/>` | Entity reference |
| `contact_sport` table | `<m2mrelationship name="contact_sport">` | M2M mapping |
| `partylist_attendees` table | `<field name="attendees"><partylistmember>...` | Nested relationship |
| `regardingobjectid_entityreference = "account"` | `lookupentity="account"` | Polymorphic type |
