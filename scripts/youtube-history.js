// [[file:../org/youtube.org::*YouTube website history][YouTube website history:1]]
const DAYS = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

const MONTHS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

function parseDayString(day) {
  const today = new Date();
  today.setUTCHours(0);
  today.setUTCMinutes(0);
  today.setUTCSeconds(0);
  today.setUTCMilliseconds(0);
  if (day === "Today") {
    return today.toJSON();
  }
  if (day === "Yesterday") {
    today.setUTCDate(today.getUTCDate() - 1);
    return today.toJSON();
  }
  if (DAYS.includes(day)) {
    const now = today.getDay() - 1 + 7;
    const then = DAYS.indexOf(day) + 7;
    today.setUTCDate(today.getUTCDate() - (now - then));
    return today.toJSON();
  }
  return 0;
}
// YouTube website history:1 ends here

// [[file:../org/youtube.org::*YouTube website history][YouTube website history:2]]
const sleep = (m) => new Promise((r) => setTimeout(r, m));
// YouTube website history:2 ends here

// [[file:../org/youtube.org::*YouTube website history][YouTube website history:3]]
async function parseVideo(video) {
  if (!video.querySelector('#progress')) {
    await sleep(1000);
    return parseVideo(video);
  }
  const progress = parseInt(video.querySelector("#progress").style.width);
  const link = video.querySelector("#thumbnail").href;
  const id = new URL(link).searchParams.get("v");
  const channel = video.querySelector('[aria-label="Go to channel"]').href;
  return { progress, id, channel };
}
// YouTube website history:3 ends here

// [[file:../org/youtube.org::*YouTube website history][YouTube website history:4]]
async function parseDaySection(section) {
  const date = section.querySelector("#title").textContent;
  const videos = Array.from(section.querySelectorAll("ytd-video-renderer"));
  const result = [];
  for (const video of videos) {
    const datum = await parseVideo(video);
    result.push({ ...datum, date: parseDayString(date) })
  }
  return result;
}
// YouTube website history:4 ends here

// [[file:../org/youtube.org::*YouTube website history][YouTube website history:5]]
async function parseAll() {
  const root = document
    .querySelector("ytd-section-list-renderer")
    .querySelector("#contents");
  const res = [];
  let wait = 0;
  let index = 0;
  while (true) {
    const children = Array.from(root.childNodes)
      .filter((n) => n.tagName !== "YTD-CONTINUATION-ITEM-RENDERER")
      .slice(index);
    if (children.length === 0) {
      window.scrollTo(0, 1000000000);
      await sleep(1000);
      if (wait < 10) {
        wait++;
        continue;
      } else {
        break;
      }
    } else {
      wait = 0;
    }
    const child = children[0];
    child.scrollIntoView();
    res.push(...(await parseDaySection(child)));
    index++;
  }
  return res;
}
// YouTube website history:5 ends here
