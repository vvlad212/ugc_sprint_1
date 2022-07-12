from uuid import UUID

person_list = [
    {'full_name': 'George Lucas', 'id': UUID('a5a8f573-3cee-4ccc-8a2b-91cb9f55250a')},
    {'full_name': 'Mark Hamill', 'id': UUID('26e83050-29ef-4163-a99d-b546cac208f8')},
    {'full_name': 'Harrison Ford', 'id': UUID('5b4bf1bc-3397-4e83-9b17-8b10c6544ed1')},
    {'full_name': 'Carrie Fisher', 'id': UUID('b5d2b63a-ed1f-4e46-8320-cf52a32be358')},
    {'full_name': 'Peter Cushing', 'id': UUID('e039eedf-4daf-452a-bf92-a0085c68e156')},
    {'full_name': 'Irvin Kershner', 'id': UUID('1989ed1e-0c0b-4872-9dfb-f5ed13c764e2')},
    {'full_name': 'Leigh Brackett', 'id': UUID('ed149438-4d76-45c9-861b-d3ed48ccbf0c')},
    {'full_name': 'Lawrence Kasdan', 'id': UUID('3217bc91-bcfc-44eb-a609-82d228115c50')},
    {'full_name': 'Billy Dee Williams', 'id': UUID('efdd1787-8871-4aa9-b1d7-f68e55b913ed')},
    {'full_name': 'Richard Marquand', 'id': UUID('3214cf58-8dbf-40ab-9185-77213933507e')},
    {'full_name': 'J.J. Abrams', 'id': UUID('a1758395-9578-41af-88b8-3f9456e6d938')},
    {'full_name': 'Michael Arndt', 'id': UUID('cec00f0e-200b-4b48-9ed1-2f8fc3c67427')},
    {'full_name': 'Adam Driver', 'id': UUID('2d6f6284-13ce-4d25-9453-c4335432c116')},
    {'full_name': 'Jake Lloyd', 'id': UUID('979996d5-ef97-427d-a0f5-d640cd1813a4')},
    {'full_name': 'Liam Neeson', 'id': UUID('39abe5bd-33b3-44e8-8c12-2e360e2fa621')},
    {'full_name': 'Ewan McGregor', 'id': UUID('69b02c62-a329-414d-83c6-ca54be34de24')},
    {'full_name': 'Natalie Portman', 'id': UUID('c777f646-dae0-466f-867a-bc535a0b021b')},
    {'full_name': 'Hayden Christensen', 'id': UUID('62df10e8-244d-4c31-b396-564dfbc2f9c5')},
    {'full_name': 'Ian McDiarmid', 'id': UUID('7214e401-bb43-4da2-9e7a-cd6ca31ee8ca')},
    {'full_name': 'Jonathan Hales', 'id': UUID('8c220eeb-8022-44d5-8435-1f8edf258ac7')},
    {'full_name': 'Christopher Lee', 'id': UUID('ef1e2ad4-df4f-4fe0-8fa9-b8db690c4a19')},
    {'full_name': 'Christopher Leedov', 'id': UUID('ef1e2ad4-df4f-4fe0-8fa9-b8db690c4a00')},
    {'full_name': 'Roberto Orci', 'id': UUID('9b58c99a-e5a3-4f24-8f67-a038665758d6')},
    {'full_name': 'Alex Kurtzman', 'id': UUID('82b7dffe-6254-4598-b6ef-5be747193946')},
    {'full_name': 'Gene Roddenberry', 'id': UUID('6960e2ca-889f-41f5-b728-1e7313e54d6c')},
    {'full_name': 'Chris Pine', 'id': UUID('9f38323f-5912-40d2-a90c-b56899746f2a')},
    {'full_name': 'Zachary Quinto', 'id': UUID('8a34f121-7ce6-4021-b467-abec993fc6cd')},
    {'full_name': 'Leonard Nimoy', 'id': UUID('5a3d0299-2df2-4070-9fda-65ff4dfa863c')},
    {'full_name': 'Eric Bana', 'id': UUID('959d148c-022b-427f-a68b-bbe58674fe65')},
    {'full_name': 'Rian Johnson', 'id': UUID('b66db341-5dcd-4aaf-b536-050b59979357')},
    {'full_name': 'Daisy Ridley', 'id': UUID('7026c3f4-d7b8-414a-99d5-06de1788a0ee')},
    {'full_name': 'Gareth Edwards', 'id': UUID('189f1d17-c928-492a-aa33-2212b5ad1555')},
    {'full_name': 'Chris Weitz', 'id': UUID('06d3686f-56e0-40df-81ea-af95a203b58a')},
    {'full_name': 'Tony Gilroy', 'id': UUID('6d9a226f-85ca-4270-9f26-7d1b1cc7b444')},
    {'full_name': 'John Knoll', 'id': UUID('5bd4381f-5763-474f-baa0-f7f62a0819f9')},
    {'full_name': 'Gary Whitta', 'id': UUID('e0dd7338-b686-465c-93da-c9b2c57d46bb')},
    {'full_name': 'Felicity Jones', 'id': UUID('ccb3418a-d3e2-4878-a355-6f720211f39f')},
    {'full_name': 'Diego Luna', 'id': UUID('ac44d92b-7de3-4274-908f-0173e6ba310b')},
    {'full_name': 'Alan Tudyk', 'id': UUID('c59c5caf-5ca9-430e-bde5-f5141de25cb6')},
    {'full_name': 'Donnie Yen', 'id': UUID('6e2f9652-460b-4c6a-b527-5c05b40965fe')},
    {'full_name': 'Damon Lindelof', 'id': UUID('dbac6947-e620-4f92-b6a1-dae9a3b07422')},
    {'full_name': 'Zoe Saldana', 'id': UUID('4a416628-4a36-431c-9121-513674dae840')},
    {'full_name': 'Karl Urban', 'id': UUID('afa7c253-6702-47d7-a451-cf2bc9350310')},
    {'full_name': 'Chris Terrio', 'id': UUID('cdf3ace6-802d-4620-b875-809e6318a493')},
    {'full_name': 'Derek Connolly', 'id': UUID('26e020b4-98d9-4c78-b85a-0570eb19d9bc')},
    {'full_name': 'Colin Trevorrow', 'id': UUID('5623ae85-91ff-44f1-b46d-21c9d1d0d7f6')},
    {'full_name': 'Bradley Cooper', 'id': UUID('5c360057-c51f-4376-bdf5-049b87fa853b')},
    {'full_name': 'Eric Roth', 'id': UUID('39276c87-27ec-42f3-a573-e0184fc463a7')},
    {'full_name': 'Will Fetters', 'id': UUID('dd0d82d8-1c95-4bb9-b9c6-d707773aa4db')},
    {'full_name': 'Moss Hart', 'id': UUID('7fb9ae3d-aeac-40a9-aa25-cd6992be16a6')},
    {'full_name': 'John Gregory Dunne', 'id': UUID('2b0f84fb-416b-4c30-80db-69478bf872be')}]

film_by_person = [
    {'id': '3d825f60-9fff-4dfe-b294-1a45fa1e115d', 'title': 'Star Wars: Episode IV - A New Hope', 'imdb_rating': 8.6},
    {'id': '0312ed51-8833-413f-bff5-0e139c11264a', 'title': 'Star Wars: Episode V - The Empire Strikes Back',
     'imdb_rating': 8.7},
    {'id': '025c58cd-1b7e-43be-9ffb-8571a613579b', 'title': 'Star Wars: Episode VI - Return of the Jedi',
     'imdb_rating': 8.3},
    {'id': 'cddf9b8f-27f9-4fe9-97cb-9e27d4fe3394', 'title': 'Star Wars: Episode VII - The Force Awakens',
     'imdb_rating': 7.9},
    {'id': '12a8279d-d851-4eb9-9d64-d690455277cc', 'title': 'Star Wars: Episode VIII - The Last Jedi',
     'imdb_rating': 7.0},
    {'id': '46f15353-2add-415d-9782-fa9c5b8083d5', 'title': 'Star Wars: Episode IX - The Rise of Skywalker',
     'imdb_rating': 6.7},
    {'id': '134989c3-3b20-4ae7-8092-3e8ad2333d59', 'title': 'The Star Wars Holiday Special', 'imdb_rating': 2.1},
    {'id': 'f241a62c-2157-432a-bbeb-9c579c8bc18b', 'title': 'Star Wars: Episode IV: A New Hope - Deleted Scenes',
     'imdb_rating': 8.4},
    {'id': '4f53452f-a402-4a76-89fd-f034eeb8d657',
     'title': 'Star Wars: Episode V - The Empire Strikes Back: Deleted Scenes', 'imdb_rating': 7.6}]

test_films_list = [
    {
        "id": "2a090dde-f688-46fe-a9f4-b781a985275e",
        "imdb_rating": 9.6,
        "genre": [
            "Action",
            "Adventure",
            "Fantasy"
        ],
        "title": "Test title movie 1",
        "description": "Test description 1",
        "director": "Test director 1",
        "actors": [
            {
                "id": "00395304-dd52-4c7b-be0d-c2cd7a495684",
                "name": "Test actor 1"
            },
        ],
        "writers": [
            {
                "id": "1bc82e3e-d9ea-4da0-a5ea-69ba20b94373",
                "name": "Test writer 1"
            },
        ]
    },
    {
        "id": "c241874f-53d3-411a-8894-37c19d8bf010",
        "imdb_rating": 9.5,
        "genre": [
            "Action",
            "Fantasy",
            "Sci-Fi",
            "Short"
        ],
        "title": "Test title movie 2",
        "description": "Test description 2",
        "director": "Test director 2",
        "actors": [
            {
                "id": "3683c176-c96e-4850-ba76-3e3a0290bf3f",
                "name": "Test actor 2"
            },
        ],
        "writers": []
    },
    {
        "id": "05d7341e-e367-4e2e-acf5-4652a8435f93",
        "imdb_rating": 9.5,
        "genre": [
            "Documentary"
        ],
        "title": "Test title movie 3",
        "description": "Test description 3",
        "director": "",
        "actors": [
            {
                "id": "901595ba-4278-4224-b04c-974c28428a08",
                "name": "Test actor 3"
            },
        ],
        "writers": []
    },
    {
        "id": "c49c1df9-6d06-47b7-87db-d96190901fa4",
        "imdb_rating": 9.4,
        "genre": [
            "Comedy",
            "Short"
        ],
        "title": "Test title 4",
        "description": "",
        "director": "Test director 4",
        "actors": [
            {
                "id": "14b21c3c-332c-4f12-aa5d-ec5d45f427c3",
                "name": "Test actor 4"
            },
        ],
        "writers": [
            {
                "id": "0695b905-3201-42d6-afee-f47929a928ef",
                "name": "Test writer 4"
            },
        ]
    },
    {
        "id": "c71db79a-6978-46da-9b89-43a92ebfceac",
        "imdb_rating": 9.2,
        "genre": [
            "Action",
            "Adventure",
            "Family"
        ],
        "title": "Test title 5",
        "description": None,
        "director": "Test director 5",
        "actors": [],
        "writers": []
    },
    {
        "id": "2e5561a2-bb7f-48d3-8249-fb668db6014a",
        "imdb_rating": 9.2,
        "genre": [
            "Action",
            "Adventure",
            "Comedy"
        ],
        "title": "Test title 6",
        "description": "Test description 6",
        "director": "Test director 6",
        "actors": [
            {
                "id": "8b223e9f-4782-489c-a277-80375aafdced",
                "name": "Test actor 6"
            },
        ],
        "writers": [
            {
                "id": "1f95b24c-c2e1-4fde-9c84-66e769b1a112",
                "name": "Test writer 6"
            },
        ]
    },

    {
        "id": "2e5561a2-bb7f-48d3-8249-fb668db6015a",
        "imdb_rating": 5.2,
        "genre": [
            "Action",
            "Adventure",
            "Comedy"
        ],
        "title": "Test title 7",
        "description": "Test description 7",
        "director": "Test director 7",
        "actors": [
            {
                "id": "8b223e9f-4782-489c-a277-80375aafdced",
                "name": "Test actor 6"
            },
        ],
        "writers": [
            {
                "id": "1f95b24c-c2e1-4fde-9c84-66e769b1a102",
                "name": "Test writer 7"
            },
        ]
    },
]

response_film_by_id = {
    "records": [
        {
            "id": "2e5561a2-bb7f-48d3-8249-fb668db6014a",
            "title": "Test title 6",
            "imdb_rating": 9.2
        },
        {
            "id": "2e5561a2-bb7f-48d3-8249-fb668db6015a",
            "title": "Test title 7",
            "imdb_rating": 5.2
        }
    ],
    "total_count": 2,
    "current_page": 1,
    "total_page": 0,
    "page_size": 20,
    "message": "Response for subscribed user"
}

search_by_name = {
    "total_count": 2,
    "current_from": 0,
    "page_size": 10,
    "records": [
        {
            "id": "ef1e2ad4-df4f-4fe0-8fa9-b8db690c4a19",
            "full_name": "Christopher Lee"
        },
        {
            "id": "ef1e2ad4-df4f-4fe0-8fa9-b8db690c4a00",
            "full_name": "Christopher Leedov"
        }
    ]
}
