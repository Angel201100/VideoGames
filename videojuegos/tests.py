"""Pruebas del CRUD, el acceso, la validación y el comando de datos de muestra."""

from io import StringIO
from unittest.mock import Mock, patch

from bson import ObjectId
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.core.management import CommandError, call_command
from django.test import TestCase
from django.urls import reverse


class VideojuegosCrudTests(TestCase):
    """Comprueba respuestas HTTP y operaciones de base usando una colección simulada."""

    def setUp(self):
        # Cada prueba inicia con una sesión válida y MongoDB sustituido por un Mock.
        self.user = get_user_model().objects.create_user(
            username="aprendiz",
            password="ClaveSegura-2026",
        )
        self.client.force_login(self.user)
        self.collection = Mock()
        self.collection_patch = patch(
            "videojuegos.views.get_collection",
            return_value=self.collection,
        )
        self.collection_patch.start()
        self.addCleanup(self.collection_patch.stop)
        self.collection.find.return_value.sort.return_value = []

    def datos_validos(self, **cambios):
        """Genera un formulario correcto y permite cambiar campos para casos límite."""
        datos = {
            "nombre": "Overcooked 2",
            "costo": "0",
            "descripcion": "Juego cooperativo de cocina.",
            "jugadores": "4",
        }
        datos.update(cambios)
        return datos

    # AUTENTICACIÓN: rutas protegidas, login, logout y método HTTP para cerrar sesión.
    def test_login_is_required_for_all_crud_routes(self):
        self.client.logout()
        urls = [
            reverse("videojuegos:listar"),
            reverse("videojuegos:crear"),
            reverse("videojuegos:editar", args=["507f1f77bcf86cd799439011"]),
            reverse("videojuegos:eliminar", args=["507f1f77bcf86cd799439011"]),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/login/", response["Location"])

    def test_user_can_log_in_and_log_out(self):
        self.client.logout()

        login_response = self.client.post(
            reverse("login"),
            {"username": "aprendiz", "password": "ClaveSegura-2026"},
        )

        self.assertRedirects(login_response, reverse("videojuegos:listar"))
        self.assertIn("_auth_user_id", self.client.session)

        logout_response = self.client.post(reverse("logout"))

        self.assertRedirects(logout_response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_page_only_shows_the_sign_in_heading_and_form(self):
        self.client.logout()

        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Iniciar sesión</h1>")
        self.assertNotContains(response, "VIDEO")
        self.assertNotContains(response, "GAMES")

    def test_logout_rejects_get_requests(self):
        response = self.client.get(reverse("logout"))

        self.assertEqual(response.status_code, 405)

    # CARGA DE DATOS: el comando inserta únicamente títulos ausentes y reporta errores.
    def test_seed_command_adds_five_games_without_overwriting_existing_data(self):
        self.collection.update_one.side_effect = [
            Mock(upserted_id=ObjectId()),
            Mock(upserted_id=None),
            Mock(upserted_id=ObjectId()),
            Mock(upserted_id=ObjectId()),
            Mock(upserted_id=None),
        ]
        output = StringIO()

        with patch(
            "videojuegos.management.commands.seed_videojuegos.get_collection",
            return_value=self.collection,
        ):
            call_command("seed_videojuegos", stdout=output)

        self.assertEqual(self.collection.update_one.call_count, 5)
        self.assertIn("3 agregados, 2 ya existían", output.getvalue())
        first_filter, first_update = self.collection.update_one.call_args_list[0].args
        self.assertEqual(first_filter, {"nombre": "Hades II"})
        self.assertIn("$setOnInsert", first_update)

    def test_seed_command_reports_missing_mongodb_configuration(self):
        output = StringIO()
        with patch(
            "videojuegos.management.commands.seed_videojuegos.get_collection",
            side_effect=ImproperlyConfigured("Falta configurar MONGO_URI."),
        ):
            with self.assertRaisesMessage(CommandError, "Falta configurar MONGO_URI"):
                call_command("seed_videojuegos", stdout=output)

    # LECTURA Y CREACIÓN: renderizado, guardado de datos válidos y validaciones.
    def test_list_renders_games_in_name_order(self):
        identifier = ObjectId()
        self.collection.find.return_value.sort.return_value = [
            {
                "_id": identifier,
                "nombre": "Overcooked 2",
                "costo": 0,
                "descripcion": "Cooperativo",
                "jugadores": 4,
            }
        ]

        response = self.client.get(reverse("videojuegos:listar"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Overcooked 2")
        self.assertContains(response, str(identifier))
        self.assertContains(response, 'class="game-card"')
        self.assertContains(response, 'class="game-price">$0</span>')
        self.assertContains(response, "4 jugadores")
        self.assertContains(response, f"Hola, <strong>{self.user.username}</strong>")
        self.assertContains(response, "Cerrar sesión")
        self.assertContains(response, "Agregar juego")
        self.assertContains(response, '<h1 id="catalog-title">Juegos</h1>')
        self.assertNotContains(response, "VIDEO")
        self.assertNotContains(response, "Encuentra tu")
        self.assertNotContains(response, "Explora el catálogo")
        self.collection.find.return_value.sort.assert_called_once_with("nombre", 1)

    def test_list_reports_missing_mongodb_configuration(self):
        with patch(
            "videojuegos.views.get_collection",
            side_effect=ImproperlyConfigured("Falta configurar MONGO_URI."),
        ):
            response = self.client.get(reverse("videojuegos:listar"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Falta configurar MONGO_URI.")

    def test_create_saves_a_valid_game_including_zero_cost(self):
        response = self.client.post(
            reverse("videojuegos:crear"),
            self.datos_validos(),
        )

        self.assertRedirects(response, reverse("videojuegos:listar"))
        saved_game = self.collection.insert_one.call_args.args[0]
        self.assertEqual(saved_game["nombre"], "Overcooked 2")
        self.assertEqual(saved_game["costo"], 0)
        self.assertEqual(saved_game["jugadores"], 4)

    def test_create_form_shows_only_the_registration_heading_and_fields(self):
        response = self.client.get(reverse("videojuegos:crear"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Registrar videojuego</h1>")
        self.assertContains(response, "Nombre del videojuego:")
        self.assertNotContains(response, "VIDEO")
        self.assertNotContains(response, "Tienda")

    def test_create_rejects_invalid_data(self):
        response = self.client.post(
            reverse("videojuegos:crear"),
            self.datos_validos(costo="-1", jugadores="4.5", descripcion=""),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "El costo debe ser un número válido")
        self.assertContains(response, "La descripción es obligatoria")
        self.assertContains(response, "debe ser un número entero")
        self.collection.insert_one.assert_not_called()

    def test_create_reports_missing_mongodb_configuration(self):
        with patch(
            "videojuegos.views.get_collection",
            side_effect=ImproperlyConfigured("Falta configurar MONGO_URI."),
        ):
            response = self.client.post(
                reverse("videojuegos:crear"),
                self.datos_validos(),
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Falta configurar MONGO_URI.")

    # EDICIÓN: actualiza solo el ObjectId indicado, admite costo cero y rechaza IDs malos.
    def test_edit_updates_only_the_selected_game(self):
        identifier = ObjectId()
        self.collection.find_one.return_value = {
            "_id": identifier,
            **self.datos_validos(),
        }

        response = self.client.post(
            reverse("videojuegos:editar", args=[str(identifier)]),
            self.datos_validos(costo="55000"),
        )

        self.assertRedirects(response, reverse("videojuegos:listar"))
        self.collection.update_one.assert_called_once_with(
            {"_id": identifier},
            {
                "$set": {
                    "nombre": "Overcooked 2",
                    "costo": 55000,
                    "descripcion": "Juego cooperativo de cocina.",
                    "jugadores": 4,
                }
            },
        )

    def test_edit_get_displays_zero_cost(self):
        identifier = ObjectId()
        self.collection.find_one.return_value = {
            "_id": identifier,
            **self.datos_validos(),
        }

        response = self.client.get(
            reverse("videojuegos:editar", args=[str(identifier)])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="0"')

    def test_edit_rejects_invalid_identifier(self):
        response = self.client.get(reverse("videojuegos:editar", args=["invalid"]))

        self.assertRedirects(response, reverse("videojuegos:listar"))
        self.collection.find_one.assert_not_called()

    # ELIMINACIÓN: requiere POST y verifica que el filtro apunte a un solo ObjectId.
    def test_delete_requires_post_and_deletes_one_game(self):
        identifier = ObjectId()
        url = reverse("videojuegos:eliminar", args=[str(identifier)])

        get_response = self.client.get(url)
        self.assertRedirects(get_response, reverse("videojuegos:listar"))
        self.collection.delete_one.assert_not_called()

        self.collection.delete_one.return_value.deleted_count = 1
        post_response = self.client.post(url)

        self.assertRedirects(post_response, reverse("videojuegos:listar"))
        self.collection.delete_one.assert_called_once_with({"_id": identifier})
