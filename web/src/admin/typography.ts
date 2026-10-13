/**
 * The kinds of text of a field, the same in the load form and in its preview, in one place so the
 * phone test can tweak them here (J2-10; the user, on the iPhone, 2026-10-13: "hay que probar").
 *
 * One size for every text of the form: titles, help, what the person types or chooses, the
 * calendar and the buttons (user, on the iPhone, 2026-10-13: "que no quede ningún tamaño de letra
 * grande, incluido los que son campos para completar o seleccionar"). The kinds differ only in
 * color. The controls used to be 16px on a touch screen so the iPhone would not zoom in on focus
 * (J1-6); that zoom is now stopped by the iOS-only viewport rule (`viewport.ts`).
 */
export const TEXT_SIZE = 'text-small pointer-coarse:text-body';

/** A field's title: the form's labels, the "Vista previa" heading and the preview's data names,
 * all in sentence case ("Criterio de aceptación"), in normal weight (user, on the iPhone,
 * 2026-10-13: the uppercase titles at a bigger size "quedó muy pesado"; this size "es el tamaño
 * correcto"), told apart from the help by its off-white color. */
export const FIELD_TITLE = `${TEXT_SIZE} font-normal text-ink`;

/** What the person types or chooses: the text of every control (the preview's values use
 * `PREVIEW_VALUE`). */
export const FIELD_VALUE = `${TEXT_SIZE} text-ink-soft`;

/** The help under a field, in the dimmest gray. */
export const FIELD_HINT = `${TEXT_SIZE} text-ink-dim`;

/** A value in the preview (and its "—" when empty): the help's size and color, so the preview
 * reads even, with its sentence-case names standing out (user, on the iPhone, 2026-10-13). Its own
 * name so it can be tuned here without touching the help. */
export const PREVIEW_VALUE = FIELD_HINT;

/** The box of every control (text field, text area, list to choose from and the help box): the
 * same frame, padding, line height and text, so none looks bigger than another. Full width and
 * never wider than its column, so a long option never pushes the page sideways on a phone. */
export const CONTROL = `block w-full min-w-0 max-w-full rounded-card border-hard border-line bg-card px-3 py-2 leading-normal outline-none focus:border-ink ${FIELD_VALUE}`;
