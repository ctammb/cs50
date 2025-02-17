SELECT people.name FROM people
    JOIN stars ON stars.person_id = people.id
    JOIN movies ON stars.movie_id = movies.id
    WHERE movies.id IN
    (SELECT stars.movie_id FROM stars WHERE stars.person_id =
    (SELECT people.id FROM people WHERE people.name = 'Kevin Bacon' AND people.birth = 1958))
    AND NOT people.name = 'Kevin Bacon';
