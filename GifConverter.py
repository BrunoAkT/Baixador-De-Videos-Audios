import argparse
import os
import shutil
import subprocess
import sys


def build_filter(fps: int, width: int | None) -> str:
	if width is None:
		return f"fps={fps},split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=bayer"

	return (
		f"fps={fps},scale={width}:-1:flags=lanczos,split[s0][s1];"
		"[s0]palettegen=stats_mode=diff[p];"
		"[s1][p]paletteuse=dither=bayer"
	)


def convert_to_gif(
	input_path: str,
	output_path: str | None,
	fps: int,
	width: int | None,
	start_time: float | None,
	duration: float | None,
) -> str:
	ffmpeg_path = shutil.which("ffmpeg")
	if ffmpeg_path is None:
		raise RuntimeError(
			"FFmpeg não encontrado no PATH. Instale o FFmpeg e adicione ao PATH do sistema."
		)

	if not os.path.isfile(input_path):
		raise FileNotFoundError(f"Arquivo de entrada não encontrado: {input_path}")

	if output_path is None:
		base_name = os.path.splitext(input_path)[0]
		output_path = f"{base_name}.gif"

	if not output_path.lower().endswith(".gif"):
		output_path = f"{output_path}.gif"

	filter_complex = build_filter(fps=fps, width=width)

	command = [ffmpeg_path, "-y"]

	if start_time is not None:
		command.extend(["-ss", str(start_time)])

	command.extend(["-i", input_path])

	if duration is not None:
		command.extend(["-t", str(duration)])

	command.extend(["-vf", filter_complex, output_path])

	result = subprocess.run(command, capture_output=True, text=True)
	if result.returncode != 0:
		error = result.stderr.strip() or "Erro desconhecido ao converter."
		raise RuntimeError(error)

	return output_path


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Converte vídeos (mp4, mkv, mov, webm etc.) para GIF usando FFmpeg."
	)
	parser.add_argument("input", help="Caminho do arquivo de vídeo de entrada")
	parser.add_argument(
		"-o",
		"--output",
		help="Caminho do GIF de saída (opcional). Padrão: mesmo nome do vídeo.",
	)
	parser.add_argument(
		"--fps",
		type=int,
		default=12,
		help="FPS do GIF (padrão: 12)",
	)
	parser.add_argument(
		"--width",
		type=int,
		default=480,
		help="Largura do GIF em pixels (padrão: 480). Use 0 para manter original.",
	)
	parser.add_argument(
		"--start",
		type=float,
		help="Segundo inicial do recorte (ex: 3.5)",
	)
	parser.add_argument(
		"--duration",
		type=float,
		help="Duração do trecho em segundos (ex: 5)",
	)
	return parser.parse_args()


def main() -> int:
	args = parse_args()
	width = None if args.width == 0 else args.width

	try:
		output = convert_to_gif(
			input_path=args.input,
			output_path=args.output,
			fps=args.fps,
			width=width,
			start_time=args.start,
			duration=args.duration,
		)
		print(f"GIF criado com sucesso: {output}")
		return 0
	except Exception as error:
		print(f"Erro: {error}", file=sys.stderr)
		return 1


if __name__ == "__main__":
	raise SystemExit(main())
