/**
 * The three kinds of text of a field, the same in the load form and in its preview, in one place
 * so the phone test can tweak them here (J2-10; the user, on the iPhone, 2026-10-13: "hay que
 * probar").
 *
 * The main size is the body size, and 16px on a touch screen: under 16px the iPhone zooms the
 * page in when a control gets the focus (J1-6). Titles and values share it, so they differ only
 * in case and color; the help is smaller and dimmer.
 */
const MAIN_SIZE = 'text-body pointer-coarse:text-[16px]';

/** A field's title: the form's labels and the preview's data names. Uppercase, a little spaced,
 * not bold, in the palette's off-white. */
export const FIELD_TITLE = `${MAIN_SIZE} font-normal uppercase tracking-[0.04em] text-ink`;

/** What the person types or chooses: the text of every control and the preview's values. */
export const FIELD_VALUE = `${MAIN_SIZE} text-ink-soft`;

/** The help under a field: smaller than the main size, in the dimmest gray. */
export const FIELD_HINT = 'text-small pointer-coarse:text-body text-ink-dim';

/** The box of every control (text field, text area, list to choose from and the help box): the
 * same frame, padding, line height and text, so none looks bigger than another. Full width and
 * never wider than its column, so a long option never pushes the page sideways on a phone. */
export const CONTROL = `block w-full min-w-0 max-w-full rounded-card border-hard border-line bg-card px-3 py-2 leading-normal outline-none focus:border-ink ${FIELD_VALUE}`;
