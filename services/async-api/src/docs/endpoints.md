
### 1. Главная страница
На ней выводятся популярные фильмы. Пока у вас есть только один признак, который можно использовать в качестве критерия популярности — imdb_rating.
#### 1.1
Схема Request Response:
```
[GET] /api/v1/films?sort=-imdb_rating
[
    {
        "uuid": "uuid",
        "title": "str",
        "imdb_rating": "float"
    },
    ...
]
```
Пример Request Response:
```
GET /api/v1/films?sort=-imdb_rating&page_size=50&page_number=1
[
    {
        "uuid": "524e4331-e14b-24d3-a156-426614174003",
        "title": "Ringo Rocket Star and His Song for Yuri Gagarin",
        "imdb_rating": 9.4
    },
    {
        "uuid": "524e4331-e14b-24d3-a156-426614174003",
        "title": "Lunar: The Silver Star",
        "imdb_rating": 9.2
    },
    ...
]
```

#### 1.2 Жанр и популярные фильмы в нём. Это просто фильтрация.

Схема Request Response:
```
[GET] /api/v1/films?sort=-imdb_rating&genre=<comedy-uuid>
[
    {
        "uuid": "uuid",
        "title": "str",
        "imdb_rating": "float"
    },
    ...
]
```
Пример Request Response:
```
GET /api/v1/films?genre=<uuid:UUID>&sort=-imdb_rating&page_size=50&page_number=1
[
    {
        "uuid": "524e4331-e14b-24d3-a156-426614174003",
        "title": "Ringo Rocket Star and His Song for Yuri Gagarin",
        "imdb_rating": 9.4
    },
    {
        "uuid": "524e4331-e14b-24d3-a156-426614174003",
        "title": "Lunar: The Silver Star",
        "imdb_rating": 9.2
    },
    ...
]
```

#### 1.3 Список жанров.

Схема Request Response:
```
[GET] /api/v1/genres/
[
    {
        "uuid": "uuid",
        "name": "str",
        ...
    },
    ...
]
```
Пример Request Response:
```
GET /api/v1/genres/
[
    {
        "uuid": "d007f2f8-4d45-4902-8ee0-067bae469161",
        "name": "Adventure",
      ...
    },
    {
        "uuid": "dc07f2f8-4d45-4902-8ee0-067bae469164",
        "name": "Fantasy",
      ...
    },
    ...
]
```

### 2 Поиск
#### 2.1 Поиск по фильмам.
Схема Request Response:
```
[GET] /api/v1/films/search/
[
    {
        "uuid": "uuid",
        "title": "str",
        "imdb_rating": "float"
    },
    ...
]
```
Пример Request Response:
```
GET /api/v1/films/search?query=star&page_number=1&page_size=50
[
    {
        "uuid": "223e4317-e89b-22d3-f3b6-426614174000",
        "title": "Billion Star Hotel",
        "imdb_rating": 6.1
    },
    {
        "uuid": "524e4331-e14b-24d3-a456-426614174001",
        "title": "Wishes on a Falling Star",
        "imdb_rating": 8.5
    },
    ...
]
```
#### 2.2 Поиск по персонам.
Схема Request Response:
```
[GET] /api/v1/persons/search/
[
    {
        "uuid": "uuid",
        "full_name": "str",
        "films": [
            {
                "uuid": "uuid",
                "roles": [
                    "str"
                ]
            },
      ...
        ]
    },
    ...
]
```
Пример Request Response:
```
GET GET /api/v1/persons/search?query=captain&page_number=1&page_size=50
[
    {
        "uuid": "724e5631-e14b-14e3-g556-888814284902",
        "full_name": "Captain Raju",
        "films": [
            {
                "uuid": "eb055946-4841-4b83-9c32-14bb1bde5de4",
                "roles": [
                    "actor"
                ]
            },
            ...
        ]
    },
    ...
]
```

### 3 Страница фильма
#### 3.1 Полная информация по фильму.
Схема Request Response:
```
[GET]  /api/v1/films/<uuid:UUID>/
{
    "uuid": "uuid",
    "title": "str",
    "imdb_rating": "float",
    "description": "str",
    "genre": [
        {
            "uuid": "uuid",
            "name": "str"
        },
      ...
    ],
    "actors": [
        {
            "uuid": "uuid",
            "full_name": "str"
        },
      ...
    ],
    "writers": [
        {
            "uuid": "uuid",
            "full_name": "str"
        },
      ...
    ],
    "directors": [
        {
            "uuid": "uuid",
            "full_name": "str"
        },
      ...
    ],
}
```
Пример Request Response:
```
GET /api/v1/films/<uuid:UUID>/
{
    "uuid": "b31592e5-673d-46dc-a561-9446438aea0f",
    "title": "Lunar: The Silver Star",
    "imdb_rating": 9.2,
    "description": "From the village of Burg, a teenager named Alex sets out to become the fabled guardian of the goddess Althena...the Dragonmaster. Along with his girlfriend Luna, and several friends they meet along the journey, they soon discover that the happy world of Lunar is on the verge of Armageddon. As Dragonmaster, Alex could save it. As a ruthless and powerful sorceror is about to play his hand, will Alex and company succeed in their quest before all is lost? And is his girlfriend Luna involved in these world shattering events? Play along and find out.",
    "genre": [
        {
            "name": "Action",
            "uuid": "6f822a92-7b51-4753-8d00-ecfedf98a937"
        },
        {
            "name": "Adventure",
            "uuid": "00f74939-18b1-42e4-b541-b52f667d50d9"
        },
        {
            "name": "Comedy",
            "uuid": "7ac3cb3b-972d-4004-9e42-ff147ede7463"
        }
    ],
    "actors": [
        {
            "uuid": "afbdbaca-04e2-44ca-8bef-da1ae4d84cdf",
            "full_name": "Ashley Parker Angel"
        },
        {
            "uuid": "3c08931f-6138-46d1-b179-1bd076b6a236",
            "full_name": "Rhonda Gibson"
        },
      ...
    ],
    "writers": [
        {
            "uuid": "1bd9a00b-9596-49a3-afbe-f39a632a09a9",
            "full_name": "Toshio Akashi"
        },
        {
            "uuid": "27fc3dc6-2656-43cb-8e56-d0dfb75ea0b2",
            "full_name": "Takashi Hino"
        },
      ...
    ],
    "directors": [
        {
            "uuid": "4a893a97-e713-4936-9dd4-c8ca437ab483",
            "full_name": "Toshio Akashi"
        },
      ...
    ],
}
```
### 4 Страница персоны.
#### 4.1 Данные по персоне.
Схема Request Response:
```
[GET] /api/v1/persons/<uuid:UUID>/
{
    "uuid": "uuid",
    "full_name": "str",
    "films": [
        {
            "uuid": "uuid",
            "roles": [
                "str"
            ]
        },
    ...
    ]
}
```
Пример Request Response:
```
GET /api/v1/persons/<uuid:UUID>
{
    "uuid": "524e4331-e14b-24d3-a456-426614174002",
    "full_name": "George Lucas",
    "films": [
        {
            "uuid": "uuid",
            "roles": [
                "writer",
                ...
            ]
        },
        ...
    ]
}
```
#### 4.2 Фильмы по персоне.
Схема Request Response:
```
[GET] /api/v1/persons/<uuid:UUID>/film/
[
    {
        "uuid": "uuid",
        "title": "str",
        "imdb_rating": "float"
    },
    ...
]
```
Пример Request Response:
```
GET /api/v1/persons/<uuid:UUID>/film
[
    {
        "uuid": "524e4331-e14b-24d3-a456-426614174001",
        "title": "Star Wars: Episode VI - Return of the Jedi",
        "imdb_rating": 8.3
    },
    {
        "uuid": "123e4317-e89b-22d3-f3b6-426614174001",
        "title": "Star Wars: Episode VII - The Force Awakens",
        "imdb_rating": 7.9
    },
    ...
]
```
### 5 Страница жанра.
Схема Request Response:
```
[GET] /api/v1/genres/<uuid:UUID>/
{
    "uuid": "uuid",
    "name": "str",
    ...
}
```
Пример Request Response:
```
GET /api/v1/genres/<uuid:UUID>
{
    "uuid": "aabbd3f3-f656-4fea-9146-63f285edf5с1",
    "name": "Action",
    ...
}
```
