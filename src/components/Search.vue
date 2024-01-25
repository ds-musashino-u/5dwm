<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { Loader } from "@googlemaps/js-api-loader";
import { ref, onMounted, onUnmounted, onActivated, onDeactivated, watch } from "vue";
import { Endpoints } from "../presenters/endpoints.mjs";
import { getAccessToken } from "../presenters/auth.mjs";
import { getCategories } from "../presenters/categories.mjs";
import { getTypes } from "../presenters/types.mjs";
import { getMedia } from "../presenters/media.mjs";
import { getUsers } from "../presenters/users.mjs";
import { GoogleMapsConfig } from "../presenters/google-maps-config.mjs";
import { search as searchWorldMap, ResultItem } from "../presenters/search.mjs";
import Time from "./Time.vue";
import ListBox from "./ListBox.vue";
import Results from "./Results.vue";
import Preview from "./Preview.vue";

const isInitializedRef = ref(false);
const isRootedRef = ref(true);
const mapRef = ref(null);
const searchPanelRef = ref(null);
const queryRef = ref("");
const isDraggingRef = ref(false);
const isLoadingRef = ref(false);
const imageIsCollapsedRef = ref(true);
const imageFileRef = ref(null);
const imageUrlRef = ref("");
const timeIsEnabledRef = ref(false);
const fromDateRef = ref(new Date());
const toDateRef = ref(new Date());
const defaultFromDateRef = ref(new Date());
const defaultToDateRef = ref(new Date());
const maxCategoriesLength = 10;
const categoriesIsCollapsedRef = ref(false);
const categoriesIsContinuousRef = ref(false);
const categoriesItemsRef = ref([]);
const categoriesPageIndexRef = ref(0);
const maxTypesLength = 25;
const typesIsCollapsedRef = ref(false);
const typesIsContinuousRef = ref(false);
const typesItemsRef = ref([]);
const typesPageIndexRef = ref(0);
const maxUsersLength = 10;
const usersIsCollapsedRef = ref(true);
const usersIsContinuousRef = ref(false);
const usersItemsRef = ref([]);
const usersPageIndexRef = ref(0);
const isSearchingRef = ref(false);
const searchPageIndexRef = ref(0);
const searchTotalCountRef = ref(null);
const searchResultsRef = ref([]);
const selectedItemRef = ref(null);
const previewPanelRef = ref(null);
const errorRef = ref(null);
const props = defineProps({
  auth0: Object,
  user: Object,
  text: String,
  isAdmin: Boolean
});
let map = null;
const searchPageLength = 100;
const searchResults = [];
const searchcCriteria = {
  keywords: [],
  categories: [],
  types: [],
  users: [],
  image: null,
  time: null,
};
const cachedSearchResults = {};
const pinnedItems = [];
const appearance = {};

fromDateRef.value.setFullYear(fromDateRef.value.getFullYear() - 1);
fromDateRef.value.setHours(0);
fromDateRef.value.setMinutes(0);
fromDateRef.value.setSeconds(0);
fromDateRef.value.setMilliseconds(0);
toDateRef.value.setHours(23);
toDateRef.value.setMinutes(59);
toDateRef.value.setSeconds(59);
toDateRef.value.setMilliseconds(0);
toDateRef.value.setDate(toDateRef.value.getDate());
defaultFromDateRef.value.setFullYear(fromDateRef.value.getFullYear());
defaultFromDateRef.value.setHours(0);
defaultFromDateRef.value.setMinutes(0);
defaultFromDateRef.value.setSeconds(0);
defaultFromDateRef.value.setMilliseconds(0);
defaultToDateRef.value.setHours(23);
defaultToDateRef.value.setMinutes(59);
defaultToDateRef.value.setSeconds(59);
defaultToDateRef.value.setMilliseconds(0);
defaultToDateRef.value.setDate(toDateRef.value.getDate());

const initialize = async () => {
  isInitializedRef.value = true;

  const loader = new Loader({
    apiKey: GoogleMapsConfig.API_KEY,
    version: GoogleMapsConfig.VERSION,
    language: navigator.language,
  });

  await loader.load();

  map = new google.maps.Map(mapRef.value, GoogleMapsConfig.MAP_OPTIONS);
  map.setOptions({ minZoom: 3, maxZoom: 20 });
};
onMounted(() => {
  initialize();
});
onUnmounted(() => {
  isInitializedRef.value = false;
});
onActivated(() => {
  if (!isInitializedRef.value) {
    initialize();
  }

  try {
    /*const categories = await getCategories();

    console.log(categories);*/
    /*console.log("insert");
    const cat = await insertCategory("foobarbaz");

    console.log(cat);

    console.log(await getCategory(cat.id));

    console.log("update");
    const cat2 = await updateCategory(cat.id, "Hogehogehoge");

    console.log(cat2);

    console.log(await getCategory(cat2.id));

    console.log("delete");

    console.log(await deleteCategory(cat2.id));

    console.log(await getCategory(cat2.id));*/
  } catch (error) {
    console.error(error);
  }

  try {
    /*const media = await getMedia("image*", "created_at", "desc", 0, 10);

    console.log(media);*/

    /*console.log(await getMedium(media[0].id));

    console.log("insert");
    const m = await insertMedium("https://5dworldmap.com/foobar.png", "image/png", ["foo", "bar"], "foo bar baz", "foobar", new Location(105.85271637244875, 21.028344772352863, "foo"));

    console.log(m);
    console.log(await getMedium(m.id));

    console.log("delete");

    console.log(await deleteMedium(m.id));
    console.log(await getMedium(m.id));*/
  } catch (error) {
    console.error(error);
  }

  try {
    /*const users = await getUsers();

    console.log(users);*/

    //console.log(await getUser(users[0].username));
  } catch (error) {
    console.error(error);
  }
});
onDeactivated(() => { });
watch(imageUrlRef, (currentValue, oldValue) => {
  if (currentValue !== null) {
    imageFileRef.value = null;
  }
});
watch(selectedItemRef, (currentValue, oldValue) => {
    errorRef.value = null;
});

const sequenceEqual = (first, second) => {
  if (first.length === second.length) {
    for (let i = 0; i < first.length; i++) {
      if (first[i] !== second[i]) {
        return false;
      }
    }

    return true;
  }

  return false;
};
const resizeImage = async (dataURL, length) => {
  try {
    return await new Promise(async (resolve1, reject1) => {
      const i = new Image();

      i.onload = () => {
        const canvas = document.createElement("canvas");

        if (i.width > i.height) {
          if (i.width > length) {
            canvas.width = length * window.devicePixelRatio;
            canvas.height =
              Math.floor((length / i.width) * i.height) *
              window.devicePixelRatio;
          } else {
            canvas.width = i.width * window.devicePixelRatio;
            canvas.height = i.height * window.devicePixelRatio;
          }
        } else if (i.height > length) {
          canvas.width =
            Math.floor((length / i.height) * i.width) * window.devicePixelRatio;
          canvas.height = length * window.devicePixelRatio;
        } else {
          canvas.width = i.width * window.devicePixelRatio;
          canvas.height = i.height * window.devicePixelRatio;
        }

        const ctx = canvas.getContext("2d");

        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = "high";
        ctx.drawImage(i, 0, 0, canvas.width, canvas.height);
        ctx.canvas.toBlob(async (blob) => {
          try {
            resolve1(
              await new Promise(async (resolve2, reject2) => {
                const reader = new FileReader();

                reader.onload = () => {
                  resolve2(reader.result);
                };
                reader.onerror = () => {
                  reject2(reader.error);
                };
                reader.readAsDataURL(blob);
              })
            );
          } catch (e) {
            reject1(e);
          }

          ctx.canvas.width = ctx.canvas.height = 0;
        }, "image/jpeg");
      };
      i.onerror = (error) => {
        reject1(error);
      };
      i.crossOrigin = "anonymous";
      i.src = dataURL;
    });
  } catch (e) {
    console.error(e);
  }

  return null;
};
const markerClick = (event) => {
  const element = searchResults.find(
    x =>
      x.marker !== null &&
      event.latLng.lat === x.marker.position.lat &&
      event.latLng.lng === x.marker.position.lng
  );

  if (element === undefined) {
    const pinnedItem = pinnedItems.find(x => x.graph.find(y => event.latLng.lat === y.position.lat && event.latLng.lng === y.position.lng) !== undefined);

    if (pinnedItem !== undefined) {
      const index = Object.keys(cachedSearchResults).find(x => cachedSearchResults[x].media.id === pinnedItem.item.media.id);

      if (index === undefined) {
        selectedItemRef.value = Object.assign({}, pinnedItem.item);
      } else {
        selectedItemRef.value = Object.assign({ index: Number(index) }, pinnedItem.item);
      }
    }
  } else {
    const index = Object.keys(cachedSearchResults).find(x => cachedSearchResults[x].media.id === element.item.media.id);

    if (index === undefined) {
      selectedItemRef.value = Object.assign({}, element.item);
    } else {
      selectedItemRef.value = Object.assign({ index: Number(index) }, element.item);
    }
  }
};
const timeEnabled = (value) => {
  timeIsEnabledRef.value = !timeIsEnabledRef.value;
};
const timeChanged = (fromDate, toDate) => {
  fromDateRef.value = fromDate;
  toDateRef.value = toDate;
};
const dragover = (event) => {
  isDraggingRef.value = true;
  event.dataTransfer.dropEffect = "copy";
};
const drop = async (event) => {
  isDraggingRef.value = false;

  for (const file of event.dataTransfer.files) {
    const name = file.name.toLowerCase();

    if (
      name.endsWith(".apng") ||
      name.endsWith(".png") ||
      name.endsWith(".jpg") ||
      name.endsWith(".jpeg") ||
      name.endsWith(".webp")
    ) {
      isLoadingRef.value = true;

      try {
        imageUrlRef.value = "";
        imageFileRef.value = {
          filename: file.name,
          dataURL: await resizeImage(
            await new Promise(function (resolve, reject) {
              const reader = new FileReader();

              reader.addEventListener("load", (e) => {
                resolve(e.target.result);
              });
              reader.addEventListener("error", (e) => {
                reject(reader.error);
              });
              reader.readAsDataURL(file);
            }),
            512
          ),
        };
      } catch (error) {
        console.error(error);
      }

      isLoadingRef.value = false;

      return;
    }
  }
};
const browse = async (event) => {
  for (const file of event.currentTarget.files) {
    const name = file.name.toLowerCase();

    if (
      name.endsWith(".apng") ||
      name.endsWith(".png") ||
      name.endsWith(".jpg") ||
      name.endsWith(".jpeg") ||
      name.endsWith(".webp")
    ) {
      isLoadingRef.value = true;

      try {
        imageUrlRef.value = "";
        imageFileRef.value = {
          filename: file.name,
          dataURL: await resizeImage(
            await new Promise(function (resolve, reject) {
              const reader = new FileReader();

              reader.onload = () => {
                resolve(reader.result);
              };
              reader.onerror = () => {
                reject(reader.error);
              };
              reader.readAsDataURL(file);
            }),
            512
          ),
        };
      } catch (error) {
        console.error(error);
      }

      isLoadingRef.value = false;

      return;
    }
  }
};
const reset = (event) => {
  imageFileRef.value = null;
};
const pasteImageUrl = async (event) => {
  try {
    const text = await navigator.clipboard.readText();

    if (text.toLowerCase().startsWith("https://")) {
      imageUrlRef.value = text;
    } else {
      shake(event.currentTarget || event.target);
    }
  } catch (error) {
    console.error(error);
  }
};
const clearImageUrl = (event) => {
  imageUrlRef.value = "";
};
const collapseCategories = () => {
  categoriesIsCollapsedRef.value = !categoriesIsCollapsedRef.value;
};
const collapseTypes = () => {
  typesIsCollapsedRef.value = !typesIsCollapsedRef.value;
};
const collapseUsers = () => {
  usersIsCollapsedRef.value = !usersIsCollapsedRef.value;
};
const clearCategories = () => {
  for (const item of categoriesItemsRef.value) {
    if (item.checked) {
      item.checked = false;
    }
  }
};
const clearTypes = () => {
  for (const item of typesItemsRef.value) {
    if (item.checked) {
      item.checked = false;
    }
  }
};
const clearUsers = () => {
  for (const item of usersItemsRef.value) {
    if (item.checked) {
      item.checked = false;
    }
  }
};
const selectCategory = (index) => {
  categoriesItemsRef.value[index].checked =
    !categoriesItemsRef.value[index].checked;
};
const selectType = (index) => {
  typesItemsRef.value[index].checked = !typesItemsRef.value[index].checked;
};
const selectUser = (index) => {
  usersItemsRef.value[index].checked = !usersItemsRef.value[index].checked;
};
const nextCategories = async (pageIndex, pageLength, isFetchingRef) => {
  if (categoriesItemsRef.value.length <= pageIndex * maxCategoriesLength) {
    isFetchingRef.value = true;

    try {
      const items = await getCategories(pageIndex * maxCategoriesLength, pageLength);
      let length;

      if (items.length > maxCategoriesLength) {
        categoriesIsContinuousRef.value = true;
        length = maxCategoriesLength;
      } else {
        categoriesIsContinuousRef.value = false;
        length = items.length;
      }

      for (let i = 0; i < length; i++) {
        categoriesItemsRef.value.push({ checked: false, name: items[i].name });
      }
    } catch (error) {
      console.error(error);
    }

    isFetchingRef.value = false;
  }

  categoriesPageIndexRef.value = pageIndex;
};
const previousCategories = async (pageIndex) => {
  categoriesIsContinuousRef.value = true;
  categoriesPageIndexRef.value = pageIndex;
};
const nextTypes = async (pageIndex, pageLength, isFetchingRef) => {
  if (typesItemsRef.value.length <= pageIndex * maxTypesLength) {
    isFetchingRef.value = true;

    try {
      const items = await getTypes(null, null, pageIndex * maxTypesLength, pageLength);
      let length;

      if (items.length > maxTypesLength) {
        typesIsContinuousRef.value = true;
        length = maxTypesLength;
      } else {
        typesIsContinuousRef.value = false;
        length = items.length;
      }

      for (let i = 0; i < length; i++) {
        typesItemsRef.value.push({ checked: false, name: items[i] });
      }
    } catch (error) {
      console.error(error);
    }

    isFetchingRef.value = false;
  }

  typesPageIndexRef.value = pageIndex;
};
const previousTypes = async (pageIndex) => {
  typesIsContinuousRef.value = true;
  typesPageIndexRef.value = pageIndex;
};
const nextUsers = async (pageIndex, pageLength, isFetchingRef) => {
  if (usersItemsRef.value.length <= pageIndex * maxUsersLength) {
    isFetchingRef.value = true;

    try {
      const items = await getUsers(pageIndex * maxUsersLength, pageLength);
      let length;

      if (items.length > maxUsersLength) {
        usersIsContinuousRef.value = true;
        length = maxUsersLength;
      } else {
        usersIsContinuousRef.value = false;
        length = items.length;
      }

      for (let i = 0; i < length; i++) {
        usersItemsRef.value.push({ checked: false, name: items[i].username });
      }
    } catch (error) {
      console.error(error);
    }

    isFetchingRef.value = false;
  }

  usersPageIndexRef.value = pageIndex;
};
const previousUsers = async (pageIndex) => {
  usersIsContinuousRef.value = true;
  usersPageIndexRef.value = pageIndex;
};
const shake = (element) => {
  element.animate(
    [
      { transform: "translate3d(0, 0, 0)" },
      { transform: "translate3d(8px, 0, 0)" },
      { transform: "translate3d(-8px, 0, 0)" },
      { transform: "translate3d(7px, 0, 0)" },
      { transform: "translate3d(-7px, 0, 0)" },
      { transform: "translate3d(6px, 0, 0)" },
      { transform: "translate3d(-6px, 0, 0)" },
      { transform: "translate3d(5px, 0, 0)" },
      { transform: "translate3d(-5px, 0, 0)" },
      { transform: "translate3d(4px, 0, 0)" },
      { transform: "translate3d(-4px, 0, 0)" },
      { transform: "translate3d(3px, 0, 0)" },
      { transform: "translate3d(-3px, 0, 0)" },
      { transform: "translate3d(2px, 0, 0)" },
      { transform: "translate3d(-2px, 0, 0)" },
      { transform: "translate3d(1px, 0, 0)" },
      { transform: "translate3d(-1px, 0, 0)" },
      { transform: "translate3d(0, 0, 0)" },
    ],
    { duration: 1000, iterations: 1 }
  );
};
const createDataMarker = (location, value, label, color) => {
  const marker = new google.maps.Marker({
    position: {
      lat: location.latitude,
      lng: location.longitude,
    },
    icon: {
      path: google.maps.SymbolPath.CIRCLE,
      scale: value,
      strokeColor: color,
      strokeOpacity: 1,
      strokeWeight: 1,
      fillColor: color,
      fillOpacity: .75
    },
    label: { text: label, fontWeight: "bold", color: "#ffffff" },
    map: map
  });
  marker.addListener("click", markerClick);

  return marker;
};
const search = async (ignoreCache = true) => {
  if (ignoreCache) {
    searchcCriteria.keywords.splice(0);
    searchcCriteria.categories.splice(0);
    searchcCriteria.types.splice(0);
    searchcCriteria.users.splice(0);
    searchcCriteria.image = null;
    searchcCriteria.time = null;

    Object.keys(cachedSearchResults).forEach((key) => {
      if ("layer" in cachedSearchResults[key]) {
        cachedSearchResults[key].layer.setMap(null);
      }

      delete cachedSearchResults[key];
    });
  }

  if (map === null) {
    shake(searchPanelRef.value);
  } else {
    const keywords = queryRef.value.split(/\s/);
    const categories = categoriesItemsRef.value
      .filter((x) => x.checked)
      .map((x) => x.name);
    const types = typesItemsRef.value
      .filter((x) => x.checked)
      .map((x) => x.name);
    const users = usersItemsRef.value
      .filter((x) => x.checked)
      .map((x) => x.name);

    if (
      keywords.every((x) => x.length === 0) &&
      categories.length === 0 &&
      types.length === 0 &&
      users.length === 0 &&
      fromDateRef.value.getTime() > toDateRef.value.getTime() &&
      imageFileRef.value === null &&
      (imageUrlRef.value.length === 0 ||
        !imageUrlRef.value.toLowerCase().startsWith("https://"))
    ) {
      shake(searchPanelRef.value);

      return;
    }

    const range = [...Array(searchPageLength).keys()].map((x) => searchPageIndexRef.value * searchPageLength + x);

    if (range.length > 0 && range.every((x) => x in cachedSearchResults)) {
      const bounds = new google.maps.LatLngBounds();

      for (const result of searchResults) {
        if (result.marker !== null) {
          result.marker.setMap(null);
        }
      }

      searchResults.splice(0);
      searchResultsRef.value.splice(0);
      selectedItemRef.value = null;

      for (const index of range) {
        const item = cachedSearchResults[index];

        if (item.media.location !== null) {
          const marker = new google.maps.Marker({
            position: {
              lat: item.media.location.latitude,
              lng: item.media.location.longitude,
            },
            map: map,
            title: item.media.description,
            label: { text: String(searchPageIndexRef.value * searchPageLength + index + 1), fontWeight: "bold", color: "#ffffff" }
          });

          marker.addListener("click", markerClick);
          bounds.extend(
            new google.maps.LatLng(
              item.media.location.latitude,
              item.media.location.longitude
            )
          );

          searchResults.push({ marker: marker, item: item });
        } else {
          searchResults.push({ marker: null, item: item });
        }

        searchResultsRef.value.push(item);
      }

      map.fitBounds(bounds);
    } else {
      const image =
        imageFileRef.value === null
          ? imageUrlRef.value.length > 0
            ? imageUrlRef.value
            : null
          : imageFileRef.value.dataURL;
      const time =
        timeIsEnabledRef.value
          ? { from: fromDateRef.value, to: toDateRef.value }
          : { from: null, to: null };
      let searchcCriteriaIsUpdated = false;

      if (
        !sequenceEqual(searchcCriteria.keywords, keywords) ||
        !sequenceEqual(searchcCriteria.categories, categories) ||
        !sequenceEqual(searchcCriteria.types, types) ||
        !sequenceEqual(searchcCriteria.users, users) ||
        searchcCriteria.image !== image ||
        (searchcCriteria.time.from === null && time.from !== null) ||
        (searchcCriteria.time.from !== null && time.from === null) ||
        (searchcCriteria.time.from !== null &&
          time.from !== null &&
          searchcCriteria.time.from.getTime() !== time.from.getTime()) ||
        (searchcCriteria.time.to === null && time.to !== null) ||
        (searchcCriteria.time.to !== null && time.to === null) ||
        (searchcCriteria.time.to !== null &&
          time.to !== null &&
          searchcCriteria.time.to.getTime() !== time.to.getTime())
      ) {
        searchcCriteria.keywords = keywords;
        searchcCriteria.categories = categories;
        searchcCriteria.types = types;
        searchcCriteria.users = users;
        searchcCriteria.image = image;
        searchcCriteria.time = time;

        searchPageIndexRef.value = 0;
        searchTotalCountRef.value = null;

        searchcCriteriaIsUpdated = true;
      }

      if (searchcCriteriaIsUpdated || range.some(x => x in cachedSearchResults === false)) {
        for (const result of searchResults) {
          if (result.marker !== null) {
            result.marker.setMap(null);
          }
        }

        if (types.length > 0 && !types.some(x => x === 'csv')) {
          for (const pinnedItem of pinnedItems) {
            for (const marker of pinnedItem.graph) {
              marker.setMap(null);
            }

            pinnedItem.graph.splice(0);
          }

          pinnedItems.splice(0);
        }

        searchResults.splice(0);
        searchResultsRef.value.splice(0);
        selectedItemRef.value = null;

        isSearchingRef.value = true;

        try {
          const [resultItems, totalCount, timestamp] = await searchWorldMap(
            await getAccessToken(props.auth0),
            keywords,
            categories,
            types,
            users,
            image,
            time.from,
            time.to,
            "created_at",
            "desc",
            image === null ? searchPageIndexRef.value * searchPageLength : 0,
            image === null ? searchPageLength : null
          );
          const bounds = new google.maps.LatLngBounds();
          let index = 0;

          Object.keys(cachedSearchResults).forEach((key) => {
            if ("layer" in cachedSearchResults[key]) {
              cachedSearchResults[key].layer.setMap(null);
            }

            delete cachedSearchResults[key];
          });

          isRootedRef.value = false;
          searchResults.splice(0);
          searchResultsRef.value.splice(0);
          searchTotalCountRef.value = totalCount;

          if (resultItems.some((x) => x.hasScore)) {
            resultItems.sort(
              (x, y) => (y.hasScore ? y.score : 0) - (x.hasScore ? x.score : 0)
            );
          }

          if (
            resultItems.length >
            searchPageIndexRef.value * searchPageLength + searchPageLength
          ) {
            for (const resultItem of resultItems.splice(0, searchPageLength)) {
              if (resultItem.media.location === null) {
                searchResults.push({ marker: null, item: resultItem });
                searchResultsRef.value.push(resultItem);
                cachedSearchResults[
                  searchPageIndexRef.value * searchPageLength + index
                ] = resultItem;
              } else {
                const marker = new google.maps.Marker({
                  position: {
                    lat: resultItem.media.location.latitude,
                    lng: resultItem.media.location.longitude,
                  },
                  map: map,
                  title: resultItem.media.description,
                  label: { text: String(searchPageIndexRef.value * searchPageLength + index + 1), fontWeight: "bold", color: "#ffffff" }
                });

                marker.addListener("click", markerClick);
                bounds.extend(
                  new google.maps.LatLng(
                    resultItem.media.location.latitude,
                    resultItem.media.location.longitude
                  )
                );

                /*const circle = new google.maps.Circle({
                  strokeColor: "#FF0000",
                  strokeOpacity: 1.0,
                  strokeWeight: 2,
                  fillColor: "#FF0000",
                  fillOpacity: 0.25,
                  map,
                  center: {
                    lat: resultItem.media.location.latitude,
                    lng: resultItem.media.location.longitude,
                  },
                  radius: 1000,
                });*/

                searchResults.push({ marker: marker, item: resultItem/*, graph: circle*/ });
                searchResultsRef.value.push(resultItem);
                cachedSearchResults[
                  searchPageIndexRef.value * searchPageLength + index
                ] = resultItem;
              }

              index++;
            }

            for (const resultItem of resultItems) {
              if (
                resultItem.media.type.startsWith("kml") ||
                resultItem.media.type.startsWith("kmz")) {
                resultItem["loading"] = false;
                resultItem["loaded"] = false;
              } else if ("data" in resultItem.media && resultItem.media.data !== null) {
                const pinnedItem = pinnedItems.find(x => x.item.media.id === resultItem.media.id);

                resultItem["loading"] = false;

                if (pinnedItem === undefined) {
                  resultItem["loaded"] = false;
                } else {
                  const min = resultItem.media.data.reduce((x, y) => Math.min(x, y.value), 0.0);
                  const max = resultItem.media.data.reduce((x, y) => Math.max(x, y.value), 0.0);
                  const span = Math.abs(min) + max;
                  const color = resultItem.media.id in appearance ? appearance[resultItem.media.id] : window.getComputedStyle(document.documentElement).getPropertyValue("--accent-color");

                  for (const marker of pinnedItem.graph) {
                    marker.setMap(null);
                  }

                  pinnedItem.item = resultItem;
                  pinnedItem.graph.splice(0);

                  for (const dataItem of resultItem.media.data) {
                    pinnedItem.graph.push(createDataMarker(dataItem.location, (dataItem.value - min) / span * 32.0, String(dataItem.value), color));
                  }

                  resultItem["loaded"] = true;
                }
              }

              cachedSearchResults[
                searchPageIndexRef.value * searchPageLength + index
              ] = resultItem;
              index++;
            }
          } else {
            for (const resultItem of resultItems) {
              if (
                resultItem.media.type.startsWith("kml") ||
                resultItem.media.type.startsWith("kmz")) {
                resultItem["loading"] = false;
                resultItem["loaded"] = false;
              } else if ("data" in resultItem.media && resultItem.media.data !== null) {
                const pinnedItem = pinnedItems.find(x => x.item.media.id === resultItem.media.id);

                resultItem["loading"] = false;

                if (pinnedItem === undefined) {
                  resultItem["loaded"] = false;
                } else {
                  const min = resultItem.media.data.reduce((x, y) => Math.min(x, y.value), 0.0);
                  const max = resultItem.media.data.reduce((x, y) => Math.max(x, y.value), 0.0);
                  const span = Math.abs(min) + max;
                  const color = resultItem.media.id in appearance ? appearance[resultItem.media.id] : window.getComputedStyle(document.documentElement).getPropertyValue("--accent-color");

                  for (const marker of pinnedItem.graph) {
                    marker.setMap(null);
                  }

                  pinnedItem.item = resultItem;
                  pinnedItem.graph.splice(0);

                  for (const dataItem of resultItem.media.data) {
                    pinnedItem.graph.push(createDataMarker(dataItem.location, (dataItem.value - min) / span * 32.0, String(dataItem.value), color));
                  }

                  resultItem["loaded"] = true;
                }
              }

              if (resultItem.media.location === null) {
                searchResults.push({ marker: null, item: resultItem });
                searchResultsRef.value.push(resultItem);
                cachedSearchResults[
                  searchPageIndexRef.value * searchPageLength + index
                ] = resultItem;
              } else {
                const marker = new google.maps.Marker({
                  position: {
                    lat: resultItem.media.location.latitude,
                    lng: resultItem.media.location.longitude,
                  },
                  map: map,
                  label: { text: String(searchPageIndexRef.value * searchPageLength + index + 1), fontWeight: "bold", color: "#ffffff" }
                });
                marker.addListener("click", markerClick);
                bounds.extend(
                  new google.maps.LatLng(
                    resultItem.media.location.latitude,
                    resultItem.media.location.longitude
                  )
                );

                /*const circle = new google.maps.Circle({
                  strokeColor: "#FF0000",
                  strokeOpacity: 1.0,
                  strokeWeight: 2,
                  fillColor: "#FF0000",
                  fillOpacity: 0.25,
                  map,
                  center: {
                    lat: resultItem.media.location.latitude,
                    lng: resultItem.media.location.longitude,
                  },
                  radius: 1000,
                });*/
                /*const circle = new google.maps.Marker({
                  position: {
                    lat: resultItem.media.location.latitude,
                    lng: resultItem.media.location.longitude,
                  },
                  icon: {
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 10,
                    strokeWeight: 1,
                    fillColor: 'blue',
                    fillOpacity: .5
                  },
                  map: map
                });*/

                searchResults.push({ marker: marker, item: resultItem/*, graph: circle*/ });
                searchResultsRef.value.push(resultItem);
                cachedSearchResults[
                  searchPageIndexRef.value * searchPageLength + index
                ] = resultItem;
              }

              index++;
            }
          }

          map.fitBounds(bounds);
        } catch (error) {
          shake(searchPanelRef.value);
          console.error(error);
        }

        isSearchingRef.value = false;
      } else {
        isRootedRef.value = false;
      }
    }
  }
};
const back = (event) => {
  if (selectedItemRef.value !== null) {
    selectedItemRef.value = null;
  } else if (searchTotalCountRef.value !== null) {
    isRootedRef.value = true;
  }
};
const selectItem = (index, item) => {
  selectedItemRef.value = Object.assign({ index: index }, item);

  map.panTo(
    new google.maps.LatLng(
      item.media.location.latitude,
      item.media.location.longitude
    )
  );
};
const loadItem = async (item) => {
  if (item.media.type.startsWith("kml") || item.media.type.startsWith("kmz")) {
    const result = searchResults.find(x => x.item.media.id === item.media.id);

    if (result !== undefined) {
      result.item.loading = item.loading = true;
      result.item.layer = new google.maps.KmlLayer(`${Endpoints.TUNNEL_URL}?url=${result.item.media.url}`, {
        suppressInfoWindows: false,
        preserveViewport: false,
        map: map
      });
      result.item.layer.status_changed = (e) => {
        result.item.loading = item.loading = false;

        if (google.maps.KmlLayerStatus.OK === result.item.layer.getStatus()) {
          result.item.loaded = item.loaded = true;
        } else {
          errorRef.value = { message: result.item.layer.getStatus(), url: "https://developers.google.com/maps/documentation/javascript/kmllayer" };
          shake(previewPanelRef.value);
        }
      };
    }
  } else if ("data" in item.media && item.media.data !== null) {
    const result = searchResults.find(x => x.item.media.id === item.media.id);

    if (result !== undefined) {
      const graph = [];
      const min = result.item.media.data.reduce((x, y) => Math.min(x, y.value), 0.0);
      const max = result.item.media.data.reduce((x, y) => Math.max(x, y.value), 0.0);
      const span = Math.abs(min) + max;
      const color = result.item.media.id in appearance ? appearance[result.item.media.id] : window.getComputedStyle(document.documentElement).getPropertyValue("--accent-color");

      for (const dataItem of result.item.media.data) {
        graph.push(createDataMarker(dataItem.location, (dataItem.value - min) / span * 32.0, String(dataItem.value), color));
      }

      pinnedItems.push({ item: result.item, graph: graph });
      result.item.loaded = item.loaded = true;
    }
  }

  /*item.layer.addListener("click", (event) => {
    const content = event.featureData.infoWindowHtml;
  });*/
  /*try {
    const response = await fetch(item.media.url, {
      method: "GET",
    });
    
    if (response.ok) {
      item.layer = new google.maps.KmlLayer(
        await new Promise(async (resolve, reject) => {
          const reader = new FileReader();

          reader.onload = () => {
            resolve(reader.result);
          };
          reader.onerror = () => {
            reject(reader.error);
          };
          reader.readAsDataURL(await response.blob());
        }),
        {
          suppressInfoWindows: true,
          preserveViewport: false,
          map: map,
        }
      );
      item.layer.status_changed = () => {
        if (google.maps.KmlLayerStatus.OK === item.layer.getStatus()) {
          item.loaded = true;
        } else {
          shake(previewPanelRef.value);
        }
      };
      item.layer.addListener("click", (event) => {
        const content = event.featureData.infoWindowHtml;
        console.log(event);
      });
    }
  } catch (e) {
    shake(previewPanelRef.value);
    console.error(e);
  }*/
};
const unloadItem = (item) => {
  if (item.media.type.startsWith("kml") || item.media.type.startsWith("kmz")) {
    const result = searchResults.find(x => x.item.media.id === item.media.id);

    if (result !== undefined) {
      result.item.layer.setMap(null);
      result.item.loaded = item.loaded = false;
    }
  } else if ("data" in item.media && item.media.data !== null) {
    const index = pinnedItems.findIndex(x => x.item.media.id === item.media.id);

    if (index >= 0) {
      for (const marker of pinnedItems[index].graph) {
        marker.setMap(null);
      }

      pinnedItems[index].graph.splice(0);
      pinnedItems[index].item.loaded = item.loaded = false;
      pinnedItems.splice(index, 1);
    }
  }
};
const nextResults = (index) => {
  searchPageIndexRef.value = index;

  search(false);
};
const previousResults = (index) => {
  searchPageIndexRef.value = index;

  search(false);
};
const colorChanged = (item, color) => {
  const index = pinnedItems.findIndex(x => x.item.media.id === item.media.id);

  appearance[item.media.id] = color;

  if (index >= 0) {
    for (const marker of pinnedItems[index].graph) {
      const icon = marker.getIcon();

      icon.strokeColor = color;
      icon.fillColor = color;

      marker.setIcon(null);
      marker.setIcon(Object.assign({}, icon));
    }
  }
};
</script>

<template>
  <div id="search">
    <div class="flyout-left">
      <div class="wrap">
        <div class="block" ref="searchPanelRef">
          <nav class="panel">
            <div class="panel-block">
              <div class="block">
                <form class="field" @submit.prevent>
                  <div class="control">
                    <input class="input is-outlined is-size-7 has-text-weight-bold" type="text" placeholder="Keywords"
                      v-model="queryRef" />
                  </div>
                </form>
              </div>
            </div>
            <div class="panel-block">
              <div class="block">
                <nav class="level is-mobile">
                  <div class="level-left">
                    <div class="level-item">
                      <h3 class="panel-heading is-uppercase is-size-7 has-text-weight-bold">
                        Image Search
                      </h3>
                    </div>
                    <transition name="fade" mode="out-in">
                      <div class="level-item" v-show="imageFileRef !== null" key="attaced">
                        <span class="icon is-primary">
                          <i class="fa-solid fa-check"></i>
                        </span>
                      </div>
                    </transition>
                  </div>
                  <div class="level-right">
                    <div class="level-item">
                      <button class="button toggle is-rounded" @click="imageIsCollapsedRef = !imageIsCollapsedRef">
                        <span class="icon is-small" v-bind:class="{ collapsed: imageIsCollapsedRef }">
                          <i class="fa-solid fa-chevron-up"></i>
                        </span>
                      </button>
                    </div>
                  </div>
                </nav>
              </div>
              <transition name="fade" mode="out-in">
                <div class="block" v-show="!imageIsCollapsedRef" key="collapse">
                  <div class="control">
                    <div class="drop" v-bind:style="{
                      animationPlayState: isDraggingRef ? 'running' : 'paused',
                    }" @dragover.prevent="dragover($event)" @dragleave.prevent="isDraggingRef = false"
                      @drop.stop.prevent="drop($event)">
                      <transition name="fade" mode="out-in">
                        <div class="image" v-if="imageFileRef === null" v-bind:key="null">
                          <div class="level">
                            <div class="level-item">
                              <label class="
                                                file
                                                button
                                                is-circle
                                                has-text-weight-bold
                                                file-label
                                              ">
                                <input class="file-input" type="file" name="upload"
                                  accept="image/apng, image/png, image/jpeg, image/webp" style="pointer-events: none"
                                  v-bind:disabled="isLoadingRef" @change="browse($event)" />
                                <div class="file-cta_">
                                  <span class="icon">
                                    <i class="fa-solid fa-file-image"></i>
                                  </span>
                                </div>
                              </label>
                            </div>
                            <div class="level-item">
                              <span class="
                                                is-size-7 is-uppercase
                                                has-text-weight-bold has-text-centered has-text-grey
                                              ">Browse or Drag & Drop</span>
                            </div>
                          </div>
                        </div>
                        <div class="image" v-else v-bind:key="imageFileRef">
                          <div class="image">
                            <picture class="image">
                              <img v-bind:src="imageFileRef.dataURL" v-bind:alt="imageFileRef.filename" />
                            </picture>
                            <div class="control">
                              <button class="button is-circle" type="button" @click="reset($event)" key="menu">
                                <span class="icon is-small has-text-danger">
                                  <i class="fa-solid fa-xmark"></i>
                                </span>
                              </button>
                            </div>
                          </div>
                        </div>
                      </transition>
                    </div>
                  </div>
                </div>
              </transition>
              <transition name="fade" mode="out-in">
                <div class="block" v-show="!imageIsCollapsedRef" key="collapse">
                  <div class="field has-addons">
                    <div class="control is-expanded">
                      <input class="input is-size-7 has-text-weight-bold" type="text" placeholder="URL"
                        v-model="imageUrlRef" />
                    </div>
                    <div class="control">
                      <button type="button" class="button" @click="pasteImageUrl($event)">
                        <span class="icon is-small">
                          <i class="fa-solid fa-paste"></i>
                        </span>
                      </button>
                    </div>
                    <div class="control">
                      <button type="button" class="button" v-bind:disabled="imageUrlRef.length === 0"
                        @click="clearImageUrl($event)">
                        <span class="icon is-small has-text-danger">
                          <i class="fa-solid fa-xmark"></i>
                        </span>
                      </button>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
            <Time name="Time" :isEnabled="timeIsEnabledRef" :fromDate="fromDateRef" :toDate="toDateRef"
              :defaultFromDate="defaultFromDateRef" :defaultToDate="defaultToDateRef" @enabled="timeEnabled"
              @changed="timeChanged" :isCollapsed="true" />
            <ListBox name="Categories" :page-length="maxCategoriesLength" :is-enabled="user !== null"
              :is-collapsed="categoriesIsCollapsedRef" :is-continuous="categoriesIsContinuousRef"
              :items="categoriesItemsRef" :page-index="categoriesPageIndexRef" @collapse="collapseCategories"
              @clear="clearCategories" @select="selectCategory" @next="nextCategories" @previous="previousCategories" />
            <ListBox name="Types" :page-length="maxTypesLength" :is-enabled="user !== null"
              :is-collapsed="typesIsCollapsedRef" :is-continuous="typesIsContinuousRef" :items="typesItemsRef"
              :page-index="typesPageIndexRef" @collapse="collapseTypes" @clear="clearTypes" @select="selectType"
              @next="nextTypes" @previous="previousTypes" />
            <!--<ListBox
                              name="Users"
                              :max-length="maxUsersLength"
                              :is-enabled="user !== null"
                              :is-collapsed="usersIsCollapsedRef"
                              :is-continuous="usersIsContinuousRef"
                              :items="usersItemsRef"
                              :page-index="usersPageIndexRef"
                              @collapse="collapseUsers"
                              @clear="clearUsers"
                              @select="selectUser"
                              @next="nextUsers"
                              @previous="previousUsers"
                            />-->
          </nav>
        </div>
      </div>
      <div class="bottom">
        <div class="block">
          <div class="panel-block">
            <div class="control">
              <button class="button is-rounded is-outlined is-fullwidth is-size-7 is-primary" type="submit"
                v-bind:disabled="user === null || !isInitializedRef || isSearchingRef" @click="search()">
                <transition name="fade" mode="out-in">
                  <span class="icon" v-if="isSearchingRef" key="searching">
                    <i class="fas fa-spinner updating"></i>
                  </span>
                  <span class="icon" v-else key="ready">
                    <i class="fa-solid fa-magnifying-glass"></i>
                  </span>
                </transition>
                <span class="is-uppercase has-text-weight-bold">Search</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="flyout-left">
      <div class="block" ref="previewPanelRef">
        <transition name="slide" mode="out-in">
          <nav class="panel" v-if="selectedItemRef !== null" :key="selectedItemRef">
            <Preview :item="selectedItemRef" :error="errorRef" :color="appearance[selectedItemRef.media.id]" @load="loadItem"
              @unload="unloadItem" @back="back" @colorChanged="colorChanged"
              v-if="selectedItemRef.media.id in appearance" />
            <Preview :item="selectedItemRef" :error="errorRef" @load="loadItem" @unload="unloadItem" @back="back"
              @colorChanged="colorChanged" />
          </nav>
          <nav class="panel" v-else key="results">
            <Results :is-fetching="isSearchingRef" :items="searchResultsRef" :count="searchTotalCountRef"
              :page-index="searchPageIndexRef" :page-length="searchPageLength" :can-back="false" :appearance="appearance"
              @select="selectItem" @next="nextResults" @previous="previousResults" @load="loadItem" @unload="unloadItem"
              @back="back" v-if="selectedItemRef === null" key="results" />
          </nav>
        </transition>
      </div>
    </div>
    <div id="map" ref="mapRef"></div>
  </div>
</template>

<style lang="scss" scoped>
#search {
  position: absolute;
  display: flex;
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  flex-direction: row;
  align-items: flex-start;
  justify-content: flex-start;
  background: transparent;

  #map {
    display: block;
    position: relative;
    width: 100%;
    height: 100%;
    background: #f5f5f5;

    button {
      border-radius: 0 !important;
    }
  }

  .flyout-left,
  .flyout-right {
    position: relative;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: flex-end;
    top: 0px;
    margin: 0;
    border-right: 1px solid hsl(0deg, 0%, 93%);
    padding: 0px;
    width: fit-content;
    height: 100%;
    max-height: 100%;
    background: transparent;

    >.wrap {
      flex-basis: auto;
      width: fit-content;
      height: 100%;
      max-height: 100%;
      overflow-x: hidden;
      overflow-y: auto;

      >.block {
        width: 320px;
        height: fit-content;

        .panel {
          background: transparent;
          border-radius: 4px;
          box-shadow: none;
          /*box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
          0 0px 0 1px rgb(10 10 10 / 2%);
        overflow: hidden;*/

          .panel-block {
            padding: 0;
            flex-direction: column;

            >.block {
              width: 100%;

              >.level {
                margin: 0;
                padding: 0;
                width: 100%;

                >.level-left>.level-item>.panel-heading {
                  margin: 0 !important;
                  padding: 0;
                  background: transparent;
                }

                >.level-right {
                  margin: 0px 0px 0px 12px;

                  button {
                    background: transparent !important;
                  }

                  button.is-rounded {
                    border-radius: 9999px !important;
                    padding: 12px !important;
                    box-shadow: none !important;

                    >span.icon {
                      margin: 0 !important;
                      width: 1rem !important;
                      height: 1rem !important;
                    }
                  }

                  button.toggle {
                    >span {
                      transform: rotate(180deg);
                    }

                    >span.collapsed {
                      transition: transform 0.5s ease;
                      transform: rotate(0deg);
                    }
                  }
                }
              }

              >.field {
                padding: 0;
              }
            }

            >.block {
              margin: 0;
              padding: 0em 0.75em;
            }

            >.block:last-child {
              margin: 0;
              padding: 0.5em 0.75em;
            }
          }

          .panel-tabs:not(:last-child),
          .panel-block:not(:last-child) {
            border-bottom: 1px solid hsl(0deg, 0%, 93%);

            .drop {
              display: flex;
              margin: 0;
              padding: 4px;
              width: 100%;
              aspect-ratio: 16 / 9;
              border-radius: 4px;
              flex-direction: column;
              align-items: center;
              justify-content: center;
              background: linear-gradient(90deg,
                  hsl(0deg, 0%, 93%) 50%,
                  transparent 50%),
                linear-gradient(90deg, hsl(0deg, 0%, 93%) 50%, transparent 50%),
                linear-gradient(0deg, hsl(0deg, 0%, 93%) 50%, transparent 50%),
                linear-gradient(0deg, hsl(0deg, 0%, 93%) 50%, transparent 50%);
              background-repeat: repeat-x, repeat-x, repeat-y, repeat-y;
              background-size: 16px 4px, 16px 4px, 4px 16px, 4px 16px;
              background-position: 0% 0%, 100% 100%, 0% 100%, 100% 0px;
              animation: selecting 10s linear infinite;
              animation-play-state: paused;
              overflow: hidden;

              div.image {
                display: flex;
                margin: 0;
                border-radius: 4px;
                padding: 0;
                width: 100%;
                height: 100%;
                background-position: 50% 50%;
                background-size: contain;
                background-repeat: no-repeat;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                overflow: hidden;
                image-rendering: -webkit-optimize-contrast;

                >picture {
                  height: 100%;
                  border-radius: 4px;
                  overflow: hidden;

                  >img {
                    object-fit: cover;
                    height: 100%;
                  }
                }

                .control {
                  position: absolute;
                  top: 0;
                  right: 0;
                  margin: 4px 4px 0px 0px;
                  width: auto !important;
                }

                .level {
                  display: flex;
                  padding: 0.5em 0.75em;
                  flex-direction: column;
                  align-items: center;
                  justify-content: center;

                  .level-item:not(:last-child) {
                    margin: 0px 0px 6px 0px;
                    padding: 0;
                  }
                }
              }

              .button {
                box-shadow: none !important;
              }

              button.is-circle,
              .button.is-circle {
                margin: 0px;
                padding: 16px !important;
                height: initial;
                border-radius: 290486px;

                span {
                  margin: 0 !important;
                  width: 0.75rem !important;
                  height: 0.75rem !important;
                  color: var(--accent-color);
                }
              }

              button.is-primary.is-circle,
              .button.is-primary.is-circle {
                border-radius: 290486px;
                overflow: hidden;
                background-color: var(--primary-background-color) !important;
                color: #ffffff !important;
                transition: 0.5s;

                span {
                  color: #ffffff !important;
                }
              }
            }
          }
        }

        button {
          border-radius: 4px;
          box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
            0 0px 0 1px rgb(10 10 10 / 2%) !important;
        }
      }
    }

    >.block {
      width: 320px;
      height: fit-content;

      .panel {
        background: transparent;
        border-radius: 4px;
        box-shadow: none;
      }
    }

    >.block {
      width: fit-content;
      height: 100%;

      >.panel {
        width: fit-content;
        height: 100%;
      }
    }

    >.block>.panel>.panel-block>.top {
      .panel-block:first-child {
        border-bottom: 1px solid hsl(0deg, 0%, 93%);
        border-radius: 0px;
      }

      >.panel>.panel-block:first-child>.level {
        padding: 0.5em 0.75em;
      }
    }

    >.bottom {
      .panel-block:last-child {
        border-top: 1px solid hsl(0deg, 0%, 93%);
        border-radius: 0px;
      }

      >.control>.level {
        padding: 0.5em 0.75em;
      }
    }

    >.top,
    >.bottom {
      flex-shrink: 0;
      width: 100%;
      height: fit-content;
      min-height: fit-content;
      overflow-x: hidden;
      overflow-y: hidden;
      box-sizing: border-box;

      >.block {
        width: 320px;
        height: fit-content;

        .panel {
          background: transparent;
          border-radius: 4px;
          box-shadow: none;
          /*box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
            0 0px 0 1px rgb(10 10 10 / 2%);
          overflow: hidden;*/

          .panel-block {
            display: flex;
            flex-direction: row;
            justify-content: flex-start;
            align-items: flex-end;
          }
        }

        button {
          box-sizing: border-box;
          border-radius: 4px;
          height: fit-content;
          box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
            0 0px 0 1px rgb(10 10 10 / 2%) !important;
        }
      }
    }

    >.top+.block {
      width: fit-content;
      height: 100%;

      >nav.panel {
        width: fit-content;
        height: 100%;
      }
    }

    .field {
      width: 100%;
      background: #ffffff;

      .control {
        margin: 0;
        display: flex;
        justify-content: flex-start;
        align-items: center;

        input {
          margin: 0;
          border: 0px none transparent;
          padding: 16px 12px 16px 12px;
          background-color: transparent;
          box-shadow: none;
          backface-visibility: hidden;
          border: 1px solid hsl(0deg, 0%, 93%);
        }

        input::placeholder {
          color: rgba(0, 0, 0, 0.5);
          text-transform: uppercase;
          text-shadow: none;
        }

        button.is-rounded {
          border-radius: 9999px !important;
        }
      }
    }

    .has-addons {
      margin: 0;
      border: 1px solid hsl(0deg, 0%, 93%);
      border-radius: 4px;

      .control>input {
        border: 0px none transparent;
      }

      .control>button {
        background: transparent;
        box-shadow: none !important;
      }
    }

    .control:not(:first-child) {
      margin: 0px 0px 0px 0.5rem;
    }

    .field:not(:last-child) {
      margin-bottom: 0rem;
    }
  }

  .flyout-right {
    position: absolute !important;
    right: 0px !important;
  }
}

@keyframes selecting {
  to {
    background-position: 100% 0%, 0% 100%, 0% 0%, 100% 100%;
  }
}
</style>
