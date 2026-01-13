from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Input, Button, Static,
    RadioSet, RadioButton
)
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive


class OneBitDitherApp(App):

    CSS = '''
    Screen {
        align: center middle;
    }
    Vertical {
        width: 80;
        padding: 1;
    }
    '''

    mode = reactive('image')

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical():
            yield Static('Mode')

            yield RadioSet(
                RadioButton('Image', id='image'),
                RadioButton('Frames', id='frames'),
                RadioButton('Video', id='video'),
                id='mode'
            )

            yield Input(placeholder='Input path', id='input_path')
            yield Input(placeholder='Output path', id='output_path')

            yield Input(placeholder='Pixelation factor', id='pixelation', type='number')
            yield Input(placeholder='Random factor', id='random', type='number')
            yield Input(placeholder='Divergence factor', id='divergence', type='number')
            yield Input(placeholder='Divergence point', id='divergence_point', type='number')

            yield Button('Run', id='run')

            yield Static('', id='status')

        yield Footer()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.mode = event.pressed.id

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'run':
            self.run_pipeline()

    def run_pipeline(self):
        input_path = self.query_one('#input_path', Input).value
        output_path = self.query_one('#output_path', Input).value

        pixelation = int(self.query_one('#pixelation', Input).value)
        random_factor = int(self.query_one('#random', Input).value)
        divergence = float(self.query_one('#divergence', Input).value)
        divergence_point = float(self.query_one('#divergence_point', Input).value)

        self.query_one('#status', Static).update(
            f'Running {self.mode} dithering...'
        )

        # Dispatch cleanly
        if self.mode == 'image':
            self.run_image(input_path, output_path, pixelation, random_factor, divergence, divergence_point)
        elif self.mode == 'frames':
            self.run_frames(input_path, output_path, pixelation, random_factor, divergence, divergence_point)
        elif self.mode == 'video':
            self.run_video(input_path, output_path, pixelation, random_factor, divergence, divergence_point)

        self.query_one('#status', Static).update('Done.')

    # These simply call your existing scripts / functions
    def run_image(self, *args):
        from one_bit_image_ditherer import dither_image_file
        dither_image_file(*args)

    def run_frames(self, *args):
        from one_bit_frames_ditherer import dither_frames
        dither_frames(*args)

    def run_video(self, *args):
        from one_bit_video_ditherer import dither_video
        dither_video(*args)


if __name__ == '__main__':
    OneBitDitherApp().run()
