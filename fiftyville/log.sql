-- Keep a log of any SQL queries you execute as you solve the mystery.
-- to find more about the crime
SELECT description FROM crime_scene_reports
    WHERE month = 7 AND day = 28
    AND street = 'Humphrey Street';
-- Theft took place at 10:15am Humphrey Street bakery
-- Three witnesses were interviewed cocncur
-- First, we'll check the bakery's security logs
SELECT activity, license_plate FROM bakery_security_logs
    WHERE year = 2021 AND month = 7 AND day = 28
    AND hour = 10 AND minute = 15;
-- nothing came back, so we'll widen the window...
SELECT activity, license_plate FROM bakery_security_logs
    WHERE year = 2021 AND month = 7 AND day = 28
    AND hour = 10 AND minute <= 30;
--yielded 2 plates on entry and 8 plates on exit within 30 minute window
--next we'll check out the interviews...
SELECT name, transcript FROM interviews WHERE year = 2021
    AND month = 7 AND day = 28;
--interviews suggest
-- 1. thief exited the bakery within 10 minutes of the theft
-- 2. Eugene knew the thief, saw him withdrawing money at the ATM on Leggett Street the morning of
-- 3. The thief called someone when exiting the bakery, talked for less than one minute.
-- Asked to purchase a plane ticket for the first flight the next morning.
-- First, we'll check the ATM records for withdrawals..
SELECT account_number, amount FROM atm_transactions
    WHERE month = 7 AND day = 28
    AND atm_location = 'Leggett Street'
    AND transaction_type = 'withdraw';
-- returned 8 possible account numbers, let's find the name associated
SELECT atm_transactions.account_number, amount, people.name FROM atm_transactions
    JOIN bank_accounts ON atm_transactions.account_number = bank_accounts.account_number
    Join people ON bank_accounts.person_id = people.id
    WHERE month = 7 AND day = 28
    AND atm_location = 'Leggett Street'
    AND transaction_type = 'withdraw';
-- Have account names: Bruce, Diana, Brooke, Kenny, Iman, Luca, Taylor, Benista
--Let's find if any match the license plate...so we'll get names from our license plate query
SELECT people.name FROM bakery_security_logs
    JOIN people ON bakery_security_logs.license_plate = people.license_plate
    WHERE year = 2021 AND month = 7 AND day = 28
    AND hour = 10 AND minute <= 30 AND activity = 'exit';
--Let's see if there's overlap
SELECT people.name FROM bakery_security_logs
    JOIN people ON bakery_security_logs.license_plate = people.license_plate
    WHERE year = 2021 AND month = 7 AND day = 28
    AND hour = 10 AND minute <= 30 AND activity = 'exit'
INTERSECT
SELECT people.name FROM atm_transactions
    JOIN bank_accounts ON atm_transactions.account_number = bank_accounts.account_number
    JOIN people ON bank_accounts.person_id = people.id
    WHERE month = 7 AND day = 28
    AND atm_location = 'Leggett Street'
    AND transaction_type = 'withdraw';
-- we ended up with 4 possible suspects: Bruce, Diana, Iman, Luca
--let's now look at phone records...
SELECT caller, receiver FROM phone_calls
    WHERE month = 7 AND day = 28
    and duration < 60;
--let's match up the callers with the suspects...
-- there are 9 callers on that day with conversations lasting for less than a minute
SELECT DISTINCT people.name FROM people
    WHERE people.name IN
        (SELECT people.name FROM people
            JOIN phone_calls ON people.phone_number = phone_calls.caller
            WHERE month = 7 AND day = 28
            and duration < 60)
    AND people.name IN
        (SELECT people.name FROM bakery_security_logs
            JOIN people ON bakery_security_logs.license_plate = people.license_plate
            WHERE year = 2021 AND month = 7 AND day = 28
            AND hour = 10 AND minute <= 30 AND activity = 'exit'
        INTERSECT
        SELECT people.name FROM atm_transactions
            JOIN bank_accounts ON atm_transactions.account_number = bank_accounts.account_number
            JOIN people ON bank_accounts.person_id = people.id
            WHERE month = 7 AND day = 28
            AND atm_location = 'Leggett Street'
            AND transaction_type = 'withdraw');
-- that leaves us with Diana and Bruce
--let's find out what flights are leaving first
-- and who's on them
SELECT hour, minute, flights.id FROM flights
    JOIN airports ON airports.id = flights.origin_airport_id
    WHERE airports.city = 'Fiftyville'
    AND month = 7 AND day = 28
    ORDER by hour, minute
    LIMIT 1;
-- first flight is at 13:49, flight # 6 - oh, that was the 28th, need to change the date to the 29th
--let's see who's on the manifest
SELECT people.name, flights.id FROM people
    JOIN passengers ON people.passport_number = passengers.passport_number
    JOIN flights ON flights.id = passengers.flight_id
    WHERE flights.id IN
    (SELECT flights.id FROM flights
    JOIN airports ON airports.id = flights.origin_airport_id
    WHERE airports.city = 'Fiftyville'
    AND month = 7 AND day = 29
    ORDER by hour, minute
    LIMIT 1);
--the only overlap is Bruce, he's the thief
-- and the destination is...
SELECT airports.city FROM airports
    JOIN flights ON flights.destination_airport_id = airports.id
    WHERE flights.id IN
    (SELECT flights.id FROM flights
        JOIN airports ON airports.id = flights.origin_airport_id
        WHERE airports.city = 'Fiftyville'
        AND month = 7 AND day = 29
        ORDER by hour, minute
        LIMIT 1);
-- and the answer is New York City
-- now who's the accomplice? let's see who Bruce called to make the reservations...
        SELECT people.name FROM people
            JOIN phone_calls ON people.phone_number = phone_calls.receiver
            WHERE phone_calls.caller IN
                (SELECT phone_calls.caller FROM phone_calls
                    WHERE people.name IN
                        (SELECT people.name FROM people
                            JOIN phone_calls ON people.phone_number = phone_calls.caller
                            WHERE month = 7 AND day = 28
                            and duration < 60)
                        AND people.name IN
                        (SELECT people.name FROM bakery_security_logs
                            JOIN people ON bakery_security_logs.license_plate = people.license_plate
                            WHERE year = 2021 AND month = 7 AND day = 28
                            AND hour = 10 AND minute <= 30 AND activity = 'exit'
                        INTERSECT
                        SELECT people.name FROM atm_transactions
                            JOIN bank_accounts ON atm_transactions.account_number = bank_accounts.account_number
                            JOIN people ON bank_accounts.person_id = people.id
                            WHERE month = 7 AND day = 28
                            AND atm_location = 'Leggett Street'
                            AND transaction_type = 'withdraw'));
-- Diana is the accomplice!
--not quite yet, that's wrong, let's simplify and double check who he spoke to
SELECT people.name, people.phone_number FROM people
    JOIN phone_calls ON people.phone_number = phone_calls.receiver
    WHERE month = 7 AND day = 28 AND duration <60 AND phone_calls.caller IN
        (SELECT people.phone_number FROM people
            JOIN phone_calls ON people.phone_number = phone_calls.caller
            WHERE people.name = 'Bruce');
-- Robin!
--and to double check...
SELECT people.name FROM people WHERE phone_number = '(367) 555-5533';
