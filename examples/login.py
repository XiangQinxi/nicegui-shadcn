"""A login page built entirely from nicegui-shadcn components.

Run it with::

    python examples/login.py

then open http://localhost:8081 and sign in with the demo credentials printed
under the card (``admin@example.com`` / ``shadcn``).  A wrong password shows the
destructive alert; the right one swaps the card for a signed-in panel.
"""

import asyncio
import os
import sys
from pathlib import Path

if __package__ in {None, ''}:  # allow ``python examples/login.py`` from the repo root
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nicegui import ui

from nicegui_shadcn import shadcn

DEMO_EMAIL = 'admin@example.com'
DEMO_PASSWORD = 'shadcn'

ui.add_head_html('<style>body { background: var(--muted); }</style>', shared=True)


@ui.page('/')
def main() -> None:
    dark = ui.dark_mode()

    with ui.column().classes('mx-auto flex min-h-screen w-full max-w-sm flex-col justify-center gap-6 p-6'):
        with shadcn.card().props('id=login-card'):
            with shadcn.card_header(classes='gap-1'):
                shadcn.card_title('Sign in')
                shadcn.card_description('Welcome back. Pick up where you left off.')

            content = shadcn.card_content(classes='grid gap-5')
            with content:
                # --- third-party sign-in ---------------------------------- #
                with ui.row().classes('w-full gap-2'):
                    shadcn.button('GitHub', variant='outline', icon='github', classes='flex-1',
                                  on_click=lambda: ui.notify('GitHub OAuth is not wired up here.'))
                    shadcn.button('Email link', variant='outline', icon='mail', classes='flex-1',
                                  on_click=lambda: ui.notify('Neither are magic links.'))

                # --- "or" rule -------------------------------------------- #
                with ui.row().classes('w-full items-center gap-3'):
                    shadcn.separator(classes='flex-1')
                    shadcn.small('or', classes='text-muted-foreground')
                    shadcn.separator(classes='flex-1')

                # --- failure feedback ------------------------------------- #
                alert = shadcn.alert(
                    variant='destructive',
                    title='Sign in failed',
                    description='That email and password combination is not right.',
                ).props('id=login-alert')
                alert.set_visibility(False)

                # --- the form --------------------------------------------- #
                with ui.column().classes('w-full gap-2'):
                    shadcn.label('Email', for_='login-email')
                    email = shadcn.input(value=DEMO_EMAIL, placeholder='you@example.com', type='email',
                                         autocomplete='username').props('id=login-email autofocus')

                with ui.column().classes('w-full gap-2'):
                    with ui.row().classes('w-full items-center justify-between'):
                        shadcn.label('Password', for_='login-password')
                        shadcn.small('Forgot password?', classes=(
                            'cursor-pointer text-muted-foreground underline underline-offset-4 '
                            'hover:text-foreground'
                        )).on('click', lambda: ui.notify('A reset link would arrive by email.'))
                    with ui.element('div').classes('relative w-full'):
                        password = shadcn.input(placeholder='••••••••', type='password',
                                                autocomplete='current-password', classes='pr-10',
                                                ).props('id=login-password')
                        eye = shadcn.button(size='icon', variant='ghost', icon='eye', classes=(
                            'absolute right-1 top-1/2 size-7 -translate-y-1/2'))
                        eye_off = shadcn.button(size='icon', variant='ghost', icon='eye-off', classes=(
                            'absolute right-1 top-1/2 size-7 -translate-y-1/2'))
                        eye_off.set_visibility(False)

                with ui.row().classes('w-full items-center gap-2'):
                    shadcn.checkbox(value=True).props('id=login-remember')
                    shadcn.label('Remember me for 30 days', for_='login-remember',
                                 classes='font-normal text-muted-foreground')

            footer = shadcn.card_footer(classes='flex-col gap-3')
            with footer:
                submit = shadcn.button('Sign in', classes='w-full')
                with ui.row().classes('w-full items-center justify-center gap-1'):
                    shadcn.muted('No account yet?')
                    shadcn.small('Create one', classes='cursor-pointer font-medium underline underline-offset-4'
                                 ).on('click', lambda: ui.notify('Sign-up is not part of this demo.'))

            # --- what replaces the form once the credentials check out --- #
            success = ui.column().classes('w-full items-center gap-3 px-6 py-4')
            with success:
                shadcn.avatar(fallback='AD', size='lg')
                shadcn.card_title('Signed in')
                shadcn.card_description(f'Welcome back, {DEMO_EMAIL}.')
                shadcn.button('Sign out', variant='outline', on_click=lambda: sign_out())
            success.set_visibility(False)

        with ui.row().classes('w-full items-center justify-center gap-3'):
            shadcn.muted(f'Demo credentials: {DEMO_EMAIL} / {DEMO_PASSWORD}')
            shadcn.button('Dark mode', variant='ghost', size='sm', icon='moon',
                          on_click=dark.toggle)

    # ------------------------------------------------------------------ #
    # Behaviour
    # ------------------------------------------------------------------ #

    def show_password(visible: bool) -> None:
        password.props['type'] = 'text' if visible else 'password'
        password.update()
        eye.set_visibility(not visible)
        eye_off.set_visibility(visible)

    eye.on('click', lambda: show_password(True))
    eye_off.on('click', lambda: show_password(False))

    async def sign_in() -> None:
        alert.set_visibility(False)
        submit.set_enabled(False)
        submit.set_text('Signing in...')
        await asyncio.sleep(0.6)  # stand-in for the round trip to an auth server
        if email.value == DEMO_EMAIL and password.value == DEMO_PASSWORD:
            content.set_visibility(False)
            footer.set_visibility(False)
            success.set_visibility(True)
            ui.notify(f'Welcome back, {email.value}', type='positive')
        else:
            alert.set_visibility(True)
            submit.set_enabled(True)
            submit.set_text('Sign in')

    def sign_out() -> None:
        success.set_visibility(False)
        content.set_visibility(True)
        footer.set_visibility(True)
        password.set_value('')
        submit.set_enabled(True)
        submit.set_text('Sign in')

    submit.on('click', sign_in)
    password.on('keydown.enter', sign_in)


ui.run(title='nicegui-shadcn · login', reload=False, show=False,
       port=int(os.environ.get('SHADCN_LOGIN_PORT', '8081')))
