SELECT title FROM movies
    JOIN stars ON stars.movie_id = movies.id
    JOIN people ON stars.person_id = people.id
    WHERE people.name = 'Bradley Cooper'
INTERSECT
SELECT title FROM movies
    JOIN stars ON stars.movie_id = movies.id
    JOIN people ON stars.person_id = people.id
    WHERE people.name = 'Jennifer Lawrence';
