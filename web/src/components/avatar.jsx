export default function Avatar({ username = "?", size = 42 }) {
  let hue = 0;
  for (const char of username) hue = (hue * 31 + char.charCodeAt(0)) % 360;
  const style = {
    width: size,
    height: size,
    fontSize: size * 0.42,
    background: `linear-gradient(135deg,
      hsl(${hue} 80% 58%), hsl(${(hue + 70) % 360} 85% 42%))`,
  };
  return (
    <div className="avatar" style={style} aria-hidden="true">
      {username[0].toUpperCase()}
    </div>
  );
}
