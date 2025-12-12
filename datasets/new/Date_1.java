public class Date {
    private int day, month, year; // Defined variables
    private enum Month {JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC}

    public Date(int day, int month, int year) { // Initialize all variables constructor
        this.day = day;
        this.month = month;
        this.year = year;

        checkDate();
    }

    public Date(Date date) { // Copy constructor
        this.day = date.day;
        this.month = date.month;
        this.year = date.year;
    }

    public Date(String date) { // String constructor
        String[] dates;

        String regex = Character.isAlphabetic(date.charAt(0)) ? " " : "/"; // MMM word case vs DD/MM/YYYY

        dates = date.split(regex); // Split using either space or slash depending on case
        if (dates.length != 3) {
            errorExit();
        }

        if (regex.equals(" ")) {
            this.month = Month.valueOf(dates[0].toUpperCase()).ordinal() + 1; // Converts the month (e.g., "AUG") to its numeric representation
            this.day = Integer.parseInt(dates[1].replace(",", "")); // Remove comma
        } else { // Regex is "/"; Parse regularly
            this.day = Integer.parseInt(dates[0]);
            this.month = Integer.parseInt(dates[1]);
        }
        this.year = Integer.parseInt(dates[2]); // Year is parsed the same for both cases

        checkDate();
    }

    private void errorExit() { // Helper function
        System.out.println("Error");
        System.exit(1);
    }

    public boolean isLeapYear() {
        if  (year % 100 == 0) {
            return (year % 400 == 0);
        }
        return (year % 4 == 0);
    }

    public void checkDate() throws IllegalArgumentException {
        // Validate month range
        if (this.month < 1 || this.month > 12) {
            throw new IllegalArgumentException("Invalid month: " + this.month);
        }

        // JAN, MAR, MAY, JUL, AUG, OCT, DEC should have 31 days
        int[] longMonths = {1, 3, 5, 7, 8, 10, 12};
        // APR, JUN, SEP, NOV should have 30 days
        int[] shortMonths = {4, 6, 9, 11};

        for (int longMonth : longMonths) {
            if (this.month == longMonth) {
                if (this.day > 31) {
                    throw new IllegalArgumentException("Error: " + getMonthName(this.month) + " has at most 31 days.");
                }
            }
        }

        for (int shortMonth : shortMonths) {
            if (this.month == shortMonth) {
                if (this.day > 30) {
                    throw new IllegalArgumentException("Error: " + getMonthName(this.month) + " has at most 30 days.");
                }
            }
        }

        // February cases
        if (this.month == 2) {
            if (isLeapYear()) {
                if (this.day > 29) {
                    throw new IllegalArgumentException("Error: February can only have 29 days (leap).");
                }
            } else {
                if (this.day > 28) {
                    throw new IllegalArgumentException("Error: February can only have 28 days");
                }
            }
        }

        if (this.day < 1 || this.day > 31) {
            throw new IllegalArgumentException("Invalid day: " + this.day);
        }

        if ((this.month == 4 || this.month == 6 || this.month == 9 || this.month == 11) && this.day > 30) {
            throw new IllegalArgumentException("Error: " + getMonthName(this.month) + " has at most 30 days.");
        }
    }

    private String getMonthName(int month) {
        String[] monthNames =
                {
                "", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
                };
        return monthNames[month];
    }


    public int getDay() {
        return day;
    }

    public void setDay(int day) {
        if (day > 0 && day <= 31) {
            this.day = day;
        }
        checkDate();
    }

    public int getMonth() {
        return month;
    }

    public void setMonth(int month) {
        if (month > 0 && month <= 12) {
            this.month = month;
        }
        checkDate();
    }

    public int getYear() {
        return year;
    }

    public void setYear(int year) {
        if (year > 0) {
            this.year = year;
        }
        checkDate();
    }

    public boolean equals(Date date) {
        return (this.day == date.day && this.month == date.month && this.year == date.year);
    }

    @Override
    public String toString() {
        return day + "/" + month + "/" + year;
    }
}
