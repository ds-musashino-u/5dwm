<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref, reactive, toRef, watch } from "vue";
const props = defineProps({
  name: { type: String, required: false, default: null },
  isEnabled: { type: Boolean, required: false, default: true },
  isCollapsed: { type: Boolean, required: false, default: false },
  isForwardEnabled: { type: Boolean, required: false, default: true },
  isBackwardEnabled: { type: Boolean, required: false, default: true },
  item: { type: Object, required: false, default: null },
  fromDate: { type: Object, required: false, default: new Date() },
  toDate: { type: Object, required: false, default: new Date() },
  defaultFromDate: { type: Object, required: false, default: new Date() },
  defaultToDate: { type: Object, required: false, default: new Date() },
});
const emit = defineEmits(["enabled", "reset", "changed"]);
const TimeUnits = {
  Year: 0,
  Month: 1,
  Day: 2,
};
const isEnabledRef = toRef(props, "isEnabled");
const isCollapsedRef = ref(props.isCollapsed);
const currentUnitRef = ref(TimeUnits.Year);
const fromDateRef = ref(new Date(props.fromDate));
const toDateRef = ref(new Date(props.toDate));
const fromYearRef = ref(props.fromDate.getFullYear());
const fromMonthRef = ref(props.fromDate.getMonth());
const fromDayRef = ref(props.fromDate.getDate());
const fromHoursRef = ref(props.fromDate.getHours());
const fromMinutesRef = ref(props.fromDate.getMinutes());
const toYearRef = ref(props.toDate.getFullYear());
const toMonthRef = ref(props.toDate.getMonth());
const toDayRef = ref(props.toDate.getDate());
const toHoursRef = ref(props.toDate.getHours());
const toMinutesRef = ref(props.toDate.getMinutes());
const hasErrorRef = ref(false);
const minDate = new Date(0, 0, 1, 0, 0, 0);
const maxDate = new Date();

minDate.setFullYear(1);

const addTime = (date, unit, value) => {
  const d = new Date(date.getTime());

  if (unit === TimeUnits.Year) {
    d.setFullYear(d.getFullYear() + value);
  } else if (unit === TimeUnits.Month) {
    d.setMonth(d.getMonth() + value);
  } else if (unit === TimeUnits.Day) {
    d.setDate(d.getDate() + value);
  }

  return d;
};
const validateForward = (date) => {
  const time = date.getTime();

  if (time <= maxDate.getTime()) {
    return true;
  }

  return false;
};
const validateBackward = (date) => {
  const time = date.getTime();

  if (minDate.getTime() < time) {
    return true;
  }

  return false;
};
const updateFromDate = (date) => {
  fromYearRef.value = date.getFullYear();
  fromMonthRef.value = date.getMonth();
  fromDayRef.value = date.getDate();
  fromHoursRef.value = date.getHours();
  fromMinutesRef.value = date.getMinutes();

  if (date.getTime() <= toDateRef.value.getTime()) {
    hasErrorRef.value = false;
  } else {
    hasErrorRef.value = true;
  }
};
const updateToDate = (date) => {
  toYearRef.value = date.getFullYear();
  toMonthRef.value = date.getMonth();
  toDayRef.value = date.getDate();
  toHoursRef.value = date.getHours();
  toMinutesRef.value = date.getMinutes();

  if (fromDateRef.value.getTime() <= date.getTime()) {
    hasErrorRef.value = false;
  } else {
    hasErrorRef.value = true;
  }
};
const hasForward = ref(
  validateForward(addTime(props.fromDate, currentUnitRef.value, 2))
);
const hasBackward = ref(
  validateBackward(addTime(props.fromDate, currentUnitRef.value, -1))
);
const reset = (event) => {
  fromDateRef.value = new Date(props.defaultFromDate);
  toDateRef.value = new Date(props.defaultToDate);

  emit("changed", props.defaultFromDate, props.defaultToDate);
};
const enabled = (event) => {
  emit("enabled");
};
const forward = (event) => {
  const fromDate = addTime(fromDateRef.value, currentUnitRef.value, 1);
  const toDate = addTime(toDateRef.value, currentUnitRef.value, 1);

  hasForward.value = validateForward(
    addTime(toDate, currentUnitRef.value, 1)
  );
  hasBackward.value = validateBackward(fromDateRef.value);

  fromDateRef.value = fromDate;
  toDateRef.value = toDate;

  emit("changed", fromDate, toDate);
};
const backward = (event) => {
  const fromDate = addTime(fromDateRef.value, currentUnitRef.value, -1);
  const toDate = addTime(toDateRef.value, currentUnitRef.value, -1);

  hasForward.value = validateForward(toDate);
  hasBackward.value = validateBackward(
    addTime(fromDate, currentUnitRef.value, -1)
  );

  fromDateRef.value = fromDate;
  toDateRef.value = toDate;

  emit("changed", fromDate, toDate);
};
const fromDateChange = (event) => {
  const date = new Date(event.currentTarget.value);

  fromDateRef.value.setFullYear(date.getFullYear());
  fromDateRef.value.setMonth(date.getMonth());
  fromDateRef.value.setDate(date.getDate());

  updateFromDate(fromDateRef.value);

  emit("changed", fromDateRef.value, toDateRef.value);
};
const fromHoursChange = (event) => {
  fromDateRef.value.setHours(Number(event.currentTarget.value));

  updateFromDate(fromDateRef.value);

  emit("changed", fromDateRef.value, toDateRef.value);
};
const fromMinutesChange = (event) => {
  fromDateRef.value.setMinutes(Number(event.currentTarget.value));

  updateFromDate(fromDateRef.value);

  emit("changed", fromDateRef.value, toDateRef.value);
};
const toDateChange = (event) => {
  const date = new Date(event.currentTarget.value);

  toDateRef.value.setFullYear(date.getFullYear());
  toDateRef.value.setMonth(date.getMonth());
  toDateRef.value.setDate(date.getDate());

  updateToDate(toDateRef.value);

  emit("changed", fromDateRef.value, toDateRef.value);
};
const toHoursChange = (event) => {
  toDateRef.value.setHours(Number(event.currentTarget.value));

  updateToDate(toDateRef.value);

  emit("changed", fromDateRef.value, toDateRef.value);
};
const toMinutesChange = (event) => {
  toDateRef.value.setMinutes(Number(event.currentTarget.value));

  updateToDate(toDateRef.value);

  emit("changed", fromDateRef.value, toDateRef.value);
};

watch(currentUnitRef, (newValue, oldValue) => {
  hasForward.value = validateForward(
    addTime(props.fromDate, currentUnitRef.value, 1)
  );
  hasBackward.value = validateBackward(
    addTime(props.fromDate, currentUnitRef.value, -1)
  );
});
watch(fromDateRef, (newValue, oldValue) => {
  if (newValue.getTime() !== oldValue.getTime()) {
    updateFromDate(newValue);
  }
});
watch(toDateRef, (newValue, oldValue) => {
  if (newValue.getTime() !== oldValue.getTime()) {
    updateToDate(newValue);
  }
});
</script>

<template>
  <div class="panel-block">
    <nav class="level is-mobile">
      <div class="level-left" v-if="name !== null">
        <div class="level-item">
          <h3 class="panel-heading is-uppercase is-size-7 has-text-weight-bold" v-text="name"></h3>
        </div>
      </div>
      <div class="level-right">
        <div class="level-item">
          <button class="button is-rounded" v-bind:disabled="
            fromDateRef.getTime() === defaultFromDate.getTime() &&
            toDateRef.getTime() === defaultToDate.getTime()
          " @click="reset($event)">
            <span class="icon is-small">
              <i class="fa-solid fa-arrow-rotate-left"></i>
            </span>
          </button>
        </div>
        <div class="level-item">
          <div class="control">
            <div class="tabs is-toggle">
              <ul>
                <li :class="{ 'is-active': !isEnabled }">
                  <a @click="isCollapsedRef = !isCollapsedRef; enabled();">
                    <span class="is-size-7 is-uppercase has-text-weight-bold">Off</span>
                  </a>
                </li>
                <li :class="{ 'is-active': isEnabled }">
                  <a @click="isCollapsedRef = !isCollapsedRef; enabled();">
                    <span class="is-size-7 is-uppercase has-text-weight-bold">On</span>
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <!--<button class="button" @click="isCollapsedRef = !isCollapsedRef; enabled();">
            <transition name="fade" mode="out-in">
              <span class="icon" v-if="isEnabled" key="on">
                <i class="fa-solid fa-toggle-on"></i>
              </span>
              <span class="icon" v-else key="off">
                <i class="fa-solid fa-toggle-off"></i>
              </span>
            </transition>
          </button>-->
        </div>
        <div class="level-item is-hidden">
          <button class="button toggle is-rounded" @click="isCollapsedRef = !isCollapsedRef">
            <span class="icon is-small" v-bind:class="{ collapsed: isCollapsedRef }">
              <i class="fa-solid fa-chevron-up"></i>
            </span>
          </button>
        </div>
      </div>
    </nav>
    <transition name="fade" mode="out-in">
      <nav class="level is-mobile" v-if="!isCollapsedRef" key="collapse">
        <div class="level-left">
          <div class="level-item">
            <button class="button is-primary" v-bind:disabled="!isEnabled || !isBackwardEnabled || !hasBackward" @click="backward($event)">
              <span class="icon is-small">
                <i class="fa-solid fa-chevron-left"></i>
              </span>
            </button>
          </div>
        </div>
        <div class="level-item">
          <div class="tabs is-toggle">
            <ul>
              <li :class="{ 'is-active': currentUnitRef === TimeUnits.Year }">
                <a @click="currentUnitRef = TimeUnits.Year">
                  <span class="is-size-7 is-uppercase has-text-weight-bold">Year</span>
                </a>
              </li>
              <li :class="{ 'is-active': currentUnitRef === TimeUnits.Month }">
                <a @click="currentUnitRef = TimeUnits.Month">
                  <span class="is-size-7 is-uppercase has-text-weight-bold">Month</span>
                </a>
              </li>
              <li :class="{ 'is-active': currentUnitRef === TimeUnits.Day }">
                <a @click="currentUnitRef = TimeUnits.Day">
                  <span class="is-size-7 is-uppercase has-text-weight-bold">Day</span>
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div class="level-right">
          <div class="level-item">
            <button class="button is-primary" v-bind:disabled="!isEnabled || !isForwardEnabled || !hasForward" @click="forward($event)">
              <span class="icon is-small">
                <i class="fa-solid fa-chevron-right"></i>
              </span>
            </button>
          </div>
        </div>
      </nav>
    </transition>
    <transition name="fade" mode="out-in">
      <nav class="level is-mobile" v-if="!isCollapsedRef" key="collapse">
        <div class="level-left">
          <div class="level-item">
            <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">From</span>
          </div>
        </div>
        <div class="level-right">
          <div class="level-item">
            <div class="field">
              <div class="control">
                <input class="input is-size-7 has-text-weight-bold" type="date"
                  v-bind:class="{ 'has-error': hasErrorRef }" v-bind:disabled="!isEnabled" v-bind:value="(Array(4).join('0') + fromYearRef).slice(-4) + '-' + (Array(2).join('0') + (fromMonthRef + 1)).slice(-2) + '-' + (Array(2).join('0') + fromDayRef).slice(-2)"
                  @change="fromDateChange" />
                <div class="select is-normal">
                  <select class="is-size-7 has-text-weight-bold" v-bind:class="{ 'has-error': hasErrorRef }"
                    v-bind:disabled="!isEnabled" @change="fromHoursChange">
                    <option v-for="i in [...Array(24).keys()]" v-bind:key="i" v-bind:selected="i === fromHoursRef"
                      v-text="i"></option>
                  </select>
                </div>
                <span class="is-size-7 is-uppercase has-text-weight-bold">:</span>
                <div class="select is-normal">
                  <select class="is-size-7 has-text-weight-bold" v-bind:class="{ 'has-error': hasErrorRef }"
                    v-bind:disabled="!isEnabled" @change="fromMinutesChange">
                    <option v-for="i in [...Array(60).keys()]" v-bind:key="i" v-bind:selected="i === fromMinutesRef"
                      v-text="i"></option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>
    </transition>
    <transition name="fade" mode="out-in">
      <nav class="level is-mobile" v-if="!isCollapsedRef" key="collapse">
        <div class="level-left">
          <div class="level-item">
            <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">To</span>
          </div>
        </div>
        <div class="level-right">
          <div class="level-item">
            <div class="field">
              <div class="control">
                <input class="input is-size-7 has-text-weight-bold" type="date"
                  v-bind:class="{ 'has-error': hasErrorRef }" v-bind:disabled="!isEnabled" v-bind:value="(Array(4).join('0') + toYearRef).slice(-4) + '-' + (Array(2).join('0') + (toMonthRef + 1)).slice(-2) + '-' + (Array(2).join('0') + toDayRef).slice(-2)"
                  @change="toDateChange" />
                <div class="select is-normal">
                  <select class="is-size-7 has-text-weight-bold" v-bind:class="{ 'has-error': hasErrorRef }"
                    v-bind:disabled="!isEnabled" @change="toHoursChange">
                    <option v-for="i in [...Array(24).keys()]" v-bind:key="i" v-bind:selected="i === toHoursRef"
                      v-text="i"></option>
                  </select>
                </div>
                <span class="is-size-7 is-uppercase has-text-weight-bold">:</span>
                <div class="select is-normal">
                  <select class="is-size-7 has-text-weight-bold" v-bind:class="{ 'has-error': hasErrorRef }"
                    v-bind:disabled="!isEnabled" @change="toMinutesChange">
                    <option v-for="i in [...Array(60).keys()]" v-bind:key="i" v-bind:selected="i === toMinutesRef"
                      v-text="i"></option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>
    </transition>
  </div>
</template>

<style lang="scss" scoped>
.panel-block {
  flex-direction: column;
  align-items: flex-start;
  padding: 0;

  >nav.level:first-child {
    background: hsl(0, 0%, 96%);
  }

  .level:first-child {
    margin: 0;
    padding: 0em 0.75em;
    width: 100%;
    flex-direction: row;

    .panel-heading {
      margin: 0;
      padding: 0;
      background: transparent;
    }

    >.level-left {
      flex-direction: column;
    }

    >.level-right {
      margin: -8px;
      flex-direction: row;
      align-items: center;

      >.level-item {
        margin: 8px;

        button {
          background: transparent !important;
        }

        .button.is-rounded {
          border-radius: 9999px !important;
          padding: 12px !important;
          box-shadow: none !important;

          >span.icon {
            margin: 0 !important;
            width: 1rem !important;
            height: 1rem !important;
          }
        }

        .control>.tabs.is-toggle {
          ul {
            margin: 0;

            >li>a {
              padding: 0.25em 0.5em;
              transition: 0.5s;
            }

            >li:not(.is-active)>a {
              background: #ffffff;
            }
          }
        }

        .button.toggle {
          >span {
            transform: rotate(180deg);
          }

          >span.collapsed {
            transition: transform 0.5s ease;
            transform: rotate(0deg);
          }
        }

        .field>.control>span {
          margin: 0;
          padding: 4px;
        }
      }

      >.level-item:nth-child(2)>button {
        padding: 8px !important;
        box-shadow: none !important;
        line-height: 1.5rem !important;
        background: transparent !important;

        >span.icon {
          margin: 0 !important;
          width: 1.5rem !important;
          height: 1.5rem !important;
          font-size: 1.5rem !important;
          line-height: 1.5rem !important;
        }
      }
    }
  }

  .level:nth-child(2) {
    border-top: 1px solid hsl(0deg, 0%, 93%);
    padding: 0.5em 0.75em 0.5em 0.75em !important;

    >.level-item {
      margin: 0;
      display: flex;
      justify-content: center;
      align-items: center;

      >.tabs>ul {
        margin: 0;

        >li>a {
          padding: 0.5em 0.5em;
          transition: 0.5s;
        }

        >li:not(.is-active)>a {
          background: #ffffff;
        }
      }
    }
  }

  .level:not(:first-child) {
    margin: 0;
    padding: 0em 0.75em 0.5em 0.75em;
    width: 100%;
    flex-direction: row;

    .panel-heading {
      margin: 0;
      padding: 0;
      background: transparent;
    }

    >.level-left {
      flex-direction: column;
    }

    >.level-right {
      margin: -8px;
      flex-direction: column;
      align-items: flex-end;

      >.level-item {
        margin: 8px;

        .button.is-rounded {
          border-radius: 9999px !important;
          padding: 12px !important;
          box-shadow: none !important;

          >span.icon {
            margin: 0 !important;
            width: 1rem !important;
            height: 1rem !important;
          }
        }

        .button.toggle {
          >span {
            transform: rotate(180deg);
          }

          >span.collapsed {
            transition: transform 0.5s ease;
            transform: rotate(0deg);
          }
        }

        .field>.control {
          >input {
            border: 1px solid hsl(0deg, 0%, 93%) !important;
            background: #ffffff;
            font-size: 0.75rem !important;
            width: calc(calc(0.75rem * 4) + calc(calc(0.75em - 1px) * 2));
          }

          >input:is([type="date"], [type="time"], [type="datetime-local"], [type="month"], [type="week"]) {
            color: #000000;
            margin: 0px 8px 0px 0px;
            border: 1px solid hsl(0deg, 0%, 93%) !important;
            background: #ffffff;
            font-size: 0.75rem !important;
            width: fit-content;
            justify-content: center;
            align-items: center;
          }

          >.select:nth-of-type(2):not(:last-of-type) {
            margin: 0px 8px 0px 0px;
            padding: 0;
          }

          >.select>select {
            border: 1px solid hsl(0deg, 0%, 93%) !important;
            background: #ffffff;
          }

          >span {
            margin: 0;
            padding: 4px 2px 4px 2px;
          }

          .has-error {
            border-color: var(--error-color);
          }
        }
      }
    }
  }

  :not(nav).level {
    align-items: flex-start;
    border-bottom: 0px none transparent;

    >.level-left {
      margin: 0;
      flex-direction: column;
      align-items: flex-start;

      .level-item:not(:last-child) {
        margin: 0px 0px 0.5em 0px;
      }
    }

    >.level-right {
      margin: 0;
      width: 50%;
      flex-direction: column;

      >.level-item {
        width: 100%;
        justify-content: flex-end;
      }

      .level-item:not(:last-child) {
        margin: 0px 0px 0.5em 0px;
      }
    }
  }

  /*.level:nth-child(even):not(:first-child) {
    justify-content: flex-end;
  }*/

  .control {
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
    padding: 0 !important;

    .level {
      padding: 0;
      width: 100%;

      >.level-item>.media {
        display: inline-block;
        margin: 0;
        border: 0px none transparent !important;
        padding: 0;
        width: 100%;

        .media-content {
          width: 100%;

          picture {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;

            img {
              object-fit: contain;
              width: 400px;
            }
          }
        }
      }
    }
  }

  .control:last-child {
    padding: 12px 0px 0px 0px;
  }

  .content {
    margin: 0;
    padding: 0.5em 0.75em;
    width: 100%;

    span+p,
    p {
      margin: 0.5em 0px 0px 0px;
      overflow-wrap: break-word;
    }
  }
}

.panel-block:not(:last-child) {
  border-bottom: 1px solid hsl(0deg, 0%, 93%);
}

.tabs.is-toggle li:first-child a {
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
}

.tabs.is-toggle li:last-child a {
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
}
</style>
