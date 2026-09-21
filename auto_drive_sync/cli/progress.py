from rich.progress import Progress, TextColumn, BarColumn, TaskID


def render_track_progress(current, total, status='Processando'):
    with Progress(
        TextColumn('[progress.description]{task.description}'),
        BarColumn(),
        TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
    ) as progress:
        task = progress.add_task(f'Música {current}/{total}', total=total, completed=0)
        for p in range(10):
            progress.update(task, completed=p * 10)