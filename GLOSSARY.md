# Contributions pipeline

The nightly jobs that read the files employers send to the scheme. They keep the member database up to date and list the contributions that are late.

## Language

### Who and what

**Employer**:
An organisation whose staff are members of the scheme. It sends the feed files and pays the contributions. Known by its employer ID.
_Avoid_: Sender, client, organisation

**Member reference**:
The scheme's identifier for a member, M and 6 digits. It is the only way to name a member outside the member database.
_Avoid_: Member ID, member number, membership number

**Joiner**:
A member whose date joined falls in the period a report covers.
_Avoid_: New starter, new entrant, new member

### Files

**Feed file**:
One file an employer sends for one feed, members or contributions, with a header and its rows.
_Avoid_: Employer file, submission, return

**Row**:
One detail record in a feed file. In a contributions file it is one payroll of one employer for one contribution period.
_Avoid_: Detail record, entry, line

**Rejected file**:
A feed file the run cannot read as a whole. Nothing in it is used, the log names it and the job exits with code 1.
_Avoid_: Refused, bad file, failed file

**Unreadable row**:
A row whose period or payment date cannot be read, in a file that is otherwise read. It is listed for Finance Ops and never dropped. The run carries on.
_Avoid_: Feed error, malformed row, rejected row, bad row, rows that could not be read

### Contributions

**Contribution period**:
The calendar month a contribution is for, written YYYY-MM.
_Avoid_: Period, pay period, contribution month

**Due date**:
The day a contribution period must be paid by: the 22nd of the next month, or the next working day when the 22nd is not one.
_Avoid_: Deadline, cut-off

**Late contribution**:
A payroll's contribution for one contribution period that was paid after the due date, or is still unpaid after it. The late contributions list shows each one with its status, paid late or unpaid, and its days late.
_Avoid_: Late payer, arrears, overdue
