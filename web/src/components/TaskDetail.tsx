import type { ReactNode } from 'react';
import type { DetailEvidence, RelatedTask, TaskDetail as Detail } from '../api';
import { shortDate, weekdayOf } from '../format';

// The detail of a task inside the app (MA-3, the user's iPhone test): opened from a card or from
// "Ver la tarea" in the chat, in Leda's own look, with "> volver" (and Telegram's "Atrás", bound
// by the page) back to the list without closing the Mini App. What it shows is what the server
// returns under the rule of who sees what (`puede_ver_tarea`): never decided here.

function day(iso: string | null): string | null {
  return iso ? `${weekdayOf(iso)} ${shortDate(iso)}` : null;
}

function Row({ label, value }: { label: string; value: string | null | undefined }) {
  if (!value) return null;
  return (
    <>
      <dt className="text-ink-dim">{label}</dt>
      <dd className="m-0 min-w-0 wrap-break-word text-ink">{value}</dd>
    </>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="flex flex-col gap-2">
      <h2 className="m-0 text-meta font-bold tracking-[0.08em] text-ink-dim">{title.toUpperCase()}</h2>
      {children}
    </section>
  );
}

function Related({ items, empty }: { items: RelatedTask[]; empty: string }) {
  if (items.length === 0) return <p className="m-0 text-body text-ink-soft">{empty}</p>;
  return (
    <ul className="m-0 flex list-none flex-col gap-1.5 p-0 text-body">
      {items.map((item, index) =>
        item.ve ? (
          <li key={index} className="min-w-0 wrap-break-word text-ink">
            {item.titulo}
            <span className="text-ink-dim">
              {' '}
              · {item.estado}
              {item.responsable ? ` · ${item.responsable}` : ''}
            </span>
          </li>
        ) : (
          <li key={index} className="text-ink-dim">
            Una tarea que no podés ver.
          </li>
        ),
      )}
    </ul>
  );
}

function Piece({ piece }: { piece: DetailEvidence }) {
  let content: ReactNode;
  if (piece.retirada) {
    content = (
      <span className="text-ink-dim">
        Retirada{piece.motivo_del_retiro ? ` (motivo: «${piece.motivo_del_retiro}»)` : ''}
      </span>
    );
  } else if (piece.clase === 'texto') {
    content = <span>«{piece.texto}»</span>;
  } else if (piece.clase === 'enlace' && piece.enlace && /^https?:\/\//.test(piece.enlace)) {
    content = (
      <a href={piece.enlace} target="_blank" rel="noopener noreferrer nofollow" className="text-ink">
        {piece.enlace}
      </a>
    );
  } else if (piece.archivo && piece.imagen) {
    content = <img src={piece.archivo} alt={piece.nombre ?? 'foto'} loading="lazy" className="block max-w-full rounded-card" />;
  } else if (piece.archivo) {
    content = (
      <a href={piece.archivo} target="_blank" rel="noopener noreferrer" className="text-ink">
        {piece.nombre ?? 'bajar el archivo'}
      </a>
    );
  } else {
    content = <span>{piece.enlace ?? piece.nombre ?? piece.texto}</span>;
  }
  return (
    <li className="flex min-w-0 flex-col gap-1 wrap-break-word">
      {content}
      <span className="text-small text-ink-dim">
        {piece.quien ?? 'Alguien del equipo'}
        {piece.cuando ? ` · ${day(piece.cuando)}` : ''}
      </span>
    </li>
  );
}

export function TaskDetail({ detail, onBack }: { detail: Detail; onBack: () => void }) {
  return (
    <article aria-label={`La tarea ${detail.titulo}`} className="flex min-w-0 flex-col gap-4">
      <div>
        <button
          type="button"
          onClick={onBack}
          className="rounded-card border-hard border-line-soft bg-transparent px-2.5 py-1 text-small text-ink-dim"
        >
          &gt; volver
        </button>
      </div>
      <h2 className="m-0 min-w-0 wrap-break-word text-day font-bold text-ink">{detail.titulo}</h2>
      <dl className="m-0 grid grid-cols-[max-content_1fr] gap-x-3 gap-y-1.5 rounded-card border-hard border-line bg-card p-3 text-body shadow-hard">
        <Row label="Estado" value={detail.estado} />
        <Row label="Vence" value={day(detail.vence) ?? 'sin fecha'} />
        <Row label="Dio para terminarla" value={day(detail.prevision)} />
        <Row label="La hace" value={detail.responsable} />
        <Row label="La revisa" value={detail.revisa ?? 'nadie'} />
        <Row label="La pidió" value={detail.pidio} />
        <Row label="Objetivo" value={detail.objetivo} />
        <Row label="Área" value={detail.area} />
      </dl>
      <Section title="Qué tiene que cumplir">
        <p className="m-0 wrap-break-word text-body text-ink">{detail.criterio || 'Sin escribir.'}</p>
      </Section>
      <Section title="Espera a">
        <Related items={detail.espera_a} empty="No espera a ninguna tarea." />
      </Section>
      <Section title="La esperan">
        <Related items={detail.la_esperan} empty="Ninguna tarea la espera." />
      </Section>
      <Section title="Lo que pide para entregarla">
        {detail.pide.length === 0 ? (
          <p className="m-0 text-body text-ink-soft">No pide evidencia.</p>
        ) : (
          <ul className="m-0 flex list-none flex-col gap-1 p-0 text-body">
            {detail.pide.map((item, index) => (
              <li key={index} className="wrap-break-word">
                {item.que}: <span className={item.cubierto ? 'text-ink' : 'text-ink-dim'}>{item.cubierto ? 'está' : 'falta'}</span>
              </li>
            ))}
          </ul>
        )}
      </Section>
      <Section title="Lo que se entregó">
        {detail.evidencia.length === 0 ? (
          <p className="m-0 text-body text-ink-soft">Todavía no se entregó nada.</p>
        ) : (
          <ul className="m-0 flex list-none flex-col gap-3 p-0 text-body">
            {detail.evidencia.map((piece, index) => (
              <Piece key={index} piece={piece} />
            ))}
          </ul>
        )}
      </Section>
    </article>
  );
}
